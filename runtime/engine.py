from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from runtime.storage import LocalJsonStore


PROCESS_STATES = [
    "draft",
    "intake_ready",
    "diagnosed",
    "restructured",
    "action_assigned",
    "checkin_received",
    "cycle_resolved",
]

ALLOWED_TRANSITIONS = {
    "draft": {"draft", "intake_ready"},
    "intake_ready": {"intake_ready", "diagnosed"},
    "diagnosed": {"restructured"},
    "restructured": {"action_assigned"},
    "action_assigned": {"action_assigned", "checkin_received"},
    "checkin_received": {"checkin_received", "cycle_resolved"},
    "cycle_resolved": set(),
}

RESOLUTION_STATUSES = {
    "none",
    "completed_shifted",
    "completed_partial",
    "completed_blocked",
}


class GuardrailError(ValueError):
    """Raised when the accepted flow or guardrails would be violated."""


@dataclass
class CycleEngine:
    store: LocalJsonStore

    def create_draft_cycle(self, user_id: str = "local-user") -> dict[str, Any]:
        profile = self.store.load_or_create_user_profile(user_id)
        if profile["created_at"] is None:
            profile["created_at"] = self._now()
        cycle_id = f"cycle-{uuid4().hex[:12]}"
        record = {
            "cycle_id": cycle_id,
            "user_id": user_id,
            "scenario_scope": "money_income",
            "process_state": "draft",
            "resolution_status": "none",
            "created_at": self._now(),
            "updated_at": self._now(),
            "intake_record": None,
            "dna_support_signals": None,
            "diagnosis_output": None,
            "old_cycle_map": None,
            "restructuring_output": None,
            "action_output": None,
            "checkin_output": None,
            "progress_snapshot": None,
        }
        profile["latest_cycle_id"] = cycle_id
        self.store.save_user_profile(profile)
        self.store.save_cycle_record(record)
        return record

    def create_cycle(
        self,
        problem_summary: str,
        repeated_pattern_summary: str,
        desired_shift: str,
        user_id: str = "local-user",
    ) -> dict[str, Any]:
        record = self.create_draft_cycle(user_id=user_id)
        self.submit_intake(
            record["cycle_id"],
            problem_summary=problem_summary,
            repeated_pattern_summary=repeated_pattern_summary,
            desired_shift=desired_shift,
        )
        self.run_diagnosis(record["cycle_id"])
        self.run_restructuring(record["cycle_id"])
        self.assign_action(record["cycle_id"])
        return self.store.load_cycle_record(record["cycle_id"])

    def submit_intake(
        self,
        cycle_id: str,
        problem_summary: str,
        repeated_pattern_summary: str,
        desired_shift: str,
    ) -> dict[str, Any]:
        record = self.store.load_cycle_record(cycle_id)
        self._require_state(record, "draft")
        if not problem_summary.strip() or not repeated_pattern_summary.strip():
            raise GuardrailError("Problem summary and repeated pattern summary are required.")
        intake = {
            "artifact_id": f"intake-{uuid4().hex[:10]}",
            "cycle_id": cycle_id,
            "captured_at": self._now(),
            "problem_summary": problem_summary.strip(),
            "repeated_pattern_summary": repeated_pattern_summary.strip(),
            "candidate_belief_language": self._extract_candidate_beliefs(problem_summary, repeated_pattern_summary),
            "candidate_behavior_clues": self._extract_behavior_clues(problem_summary, repeated_pattern_summary),
            "intake_completeness_flag": True,
            "source_excerpt": desired_shift.strip() or None,
        }
        record["intake_record"] = intake
        self._transition_process_state(record, "intake_ready")
        self._save(record)
        return record

    def run_diagnosis(self, cycle_id: str) -> dict[str, Any]:
        record = self.store.load_cycle_record(cycle_id)
        self._require_state(record, "intake_ready")
        intake = record["intake_record"]
        if not intake or not intake["intake_completeness_flag"]:
            raise GuardrailError("Cannot diagnose without a complete intake record.")
        dna = self._generate_dna_support(intake)
        diagnosis = self._generate_diagnosis(intake, dna)
        old_cycle = self._generate_old_cycle_map(diagnosis)
        record["dna_support_signals"] = dna
        record["diagnosis_output"] = diagnosis
        record["old_cycle_map"] = old_cycle
        self._transition_process_state(record, "diagnosed")
        self._save(record)
        return record

    def run_restructuring(self, cycle_id: str) -> dict[str, Any]:
        record = self.store.load_cycle_record(cycle_id)
        self._require_state(record, "diagnosed")
        diagnosis = record["diagnosis_output"]
        old_cycle = record["old_cycle_map"]
        if not diagnosis or not old_cycle:
            raise GuardrailError("Diagnosis output and old cycle map must exist before restructuring.")
        restructuring = self._generate_restructuring(diagnosis, old_cycle, record["dna_support_signals"])
        record["restructuring_output"] = restructuring
        self._transition_process_state(record, "restructured")
        self._save(record)
        return record

    def assign_action(self, cycle_id: str) -> dict[str, Any]:
        record = self.store.load_cycle_record(cycle_id)
        self._require_state(record, "restructured")
        if record["action_output"] is not None:
            raise GuardrailError("The cycle already has an action output.")
        restructuring = record["restructuring_output"]
        if not restructuring:
            raise GuardrailError("Restructuring output must exist before action assignment.")
        action = self._generate_action(restructuring)
        record["action_output"] = action
        self._transition_process_state(record, "action_assigned")
        self._save(record)
        return record

    def submit_checkin(
        self,
        cycle_id: str,
        completion_status: str,
        observed_external_result: str,
        observed_internal_reaction: str,
        old_cycle_return_note: str,
    ) -> dict[str, Any]:
        record = self.store.load_cycle_record(cycle_id)
        self._require_state(record, "action_assigned")
        if completion_status not in {"completed", "partial", "not_completed"}:
            raise GuardrailError("Unexpected completion status.")
        checkin = {
            "artifact_id": f"checkin-{uuid4().hex[:10]}",
            "cycle_id": cycle_id,
            "captured_at": self._now(),
            "completion_status": completion_status,
            "observed_external_result": observed_external_result.strip(),
            "observed_internal_reaction": observed_internal_reaction.strip(),
            "old_cycle_return_note": old_cycle_return_note.strip(),
        }
        record["checkin_output"] = checkin
        self._transition_process_state(record, "checkin_received")
        progress = self._generate_progress_snapshot(record, checkin)
        record["progress_snapshot"] = progress
        record["resolution_status"] = progress["resolution_status"]
        self._transition_process_state(record, "cycle_resolved")
        self._update_memory_record(record)
        self._save(record)
        return record

    def _transition_process_state(self, record: dict[str, Any], new_state: str) -> None:
        current = record["process_state"]
        if new_state not in PROCESS_STATES:
            raise GuardrailError(f"Unknown process state: {new_state}")
        if new_state not in ALLOWED_TRANSITIONS[current]:
            raise GuardrailError(f"Invalid transition: {current} -> {new_state}")
        if new_state == "diagnosed" and (record["diagnosis_output"] is None or record["old_cycle_map"] is None):
            raise GuardrailError("Cannot enter diagnosed without diagnosis output and old cycle map.")
        if new_state == "restructured" and record["restructuring_output"] is None:
            raise GuardrailError("Cannot enter restructured without restructuring output.")
        if new_state == "action_assigned" and record["action_output"] is None:
            raise GuardrailError("Cannot enter action_assigned without action output.")
        if new_state == "checkin_received" and record["checkin_output"] is None:
            raise GuardrailError("Cannot enter checkin_received without check-in output.")
        if new_state == "cycle_resolved":
            if record["progress_snapshot"] is None:
                raise GuardrailError("Cannot resolve a cycle without a progress snapshot.")
            if record["resolution_status"] not in RESOLUTION_STATUSES - {"none"}:
                raise GuardrailError("Cannot resolve a cycle with resolution_status=none.")
        record["process_state"] = new_state
        record["updated_at"] = self._now()

    def _require_state(self, record: dict[str, Any], expected: str) -> None:
        if record["process_state"] != expected:
            raise GuardrailError(f"Expected state {expected}, got {record['process_state']}.")

    def _extract_candidate_beliefs(self, problem_summary: str, repeated_pattern_summary: str) -> list[str]:
        text = f"{problem_summary} {repeated_pattern_summary}".lower()
        beliefs: list[str] = []
        if any(token in text for token in ("тяж", "hard", "strain", "впах", "много работ")):
            beliefs.append("money comes through strain")
        if any(token in text for token in ("цена", "просить", "ask", "price", "откаж")):
            beliefs.append("asking for more is risky")
        if not beliefs:
            beliefs.append("staying small feels safer than claiming more")
        return beliefs[:1]

    def _extract_behavior_clues(self, problem_summary: str, repeated_pattern_summary: str) -> list[str]:
        text = f"{problem_summary} {repeated_pattern_summary}".lower()
        clues: list[str] = []
        if any(token in text for token in ("работ", "впах", "overwork", "hard")):
            clues.append("adds effort instead of changing leverage")
        if any(token in text for token in ("цен", "price", "ask", "прос")):
            clues.append("avoids clean asks or clean pricing")
        if not clues:
            clues.append("stays inside familiar low-risk patterns")
        return clues[:2]

    def _generate_dna_support(self, intake: dict[str, Any]) -> dict[str, Any]:
        text = f"{intake['problem_summary']} {intake['repeated_pattern_summary']}".lower()
        cues: list[str] = []
        prohibitions: list[str] = []
        resistance: list[str] = []
        phrasing: list[str] = []
        if any(token in text for token in ("тяж", "впах", "hard", "strain")):
            cues.append("effort-heavy language")
            prohibitions.append("receiving easily feels unsafe")
            phrasing.append("avoid extreme easy-money phrasing")
        if any(token in text for token in ("цен", "price", "прос", "ask")):
            cues.append("asking-pricing tension")
            resistance.append("clean asks may trigger rejection fear")
            phrasing.append("use concrete value language")
        if not cues:
            cues.append("smallness-preservation language")
            prohibitions.append("growth may feel destabilizing")
            phrasing.append("keep reframing incremental")
        return {
            "artifact_id": f"dna-{uuid4().hex[:10]}",
            "cycle_id": intake["cycle_id"],
            "generated_at": self._now(),
            "hidden_structure_cues": cues[:2],
            "prohibition_signals": prohibitions[:1],
            "resistance_pattern_notes": resistance[:1] or ["default resistance: familiar low ceiling"],
            "likely_self_sabotage_point": "reverting to familiar low-risk effort",
            "phrasing_constraints": phrasing[:2],
        }

    def _generate_diagnosis(self, intake: dict[str, Any], dna: dict[str, Any]) -> dict[str, Any]:
        text = f"{intake['problem_summary']} {intake['repeated_pattern_summary']}".lower()
        if any(token in text for token in ("тяж", "впах", "hard", "strain", "много работ")):
            mechanism = "money_through_strain"
            old_belief = "More money comes mainly through heavier effort."
            attention = "Looks first at workload and difficulty."
            behavior = "Adds effort before changing pricing or asks."
            reinforcement = "Low result feels like proof that money is heavy."
            hidden = "Receiving with less strain feels unsafe."
        elif any(token in text for token in ("цен", "price", "прос", "ask", "откаж")):
            mechanism = "underpricing_visibility_avoidance"
            old_belief = "Asking for more puts acceptance at risk."
            attention = "Focuses on rejection signals and market resistance."
            behavior = "Delays clean asks, pricing, or clear offers."
            reinforcement = "Weak income feels like proof that asking more is dangerous."
            hidden = "Visibility may cost safety or approval."
        else:
            mechanism = "safety_in_smallness"
            old_belief = "Staying small is safer than claiming more."
            attention = "Notices reasons to stay within familiar limits."
            behavior = "Chooses low-expansion moves and keeps income ceiling intact."
            reinforcement = "Stable but low result feels safer than uncertain growth."
            hidden = "Growth may threaten emotional stability."
        return {
            "artifact_id": f"diagnosis-{uuid4().hex[:10]}",
            "cycle_id": intake["cycle_id"],
            "generated_at": self._now(),
            "leading_mechanism_hypothesis": mechanism,
            "old_belief_statement": old_belief,
            "attention_bias_clue": attention,
            "behavior_pattern_clue": behavior,
            "reinforcement_logic": reinforcement,
            "hidden_prohibition_statement": hidden,
            "diagnosis_confidence_note": f"Built from intake plus DNA cues: {', '.join(dna['hidden_structure_cues'])}",
        }

    def _generate_old_cycle_map(self, diagnosis: dict[str, Any]) -> dict[str, Any]:
        return {
            "artifact_id": f"old-cycle-{uuid4().hex[:10]}",
            "cycle_id": diagnosis["cycle_id"],
            "mapped_at": self._now(),
            "belief": diagnosis["old_belief_statement"],
            "attention": diagnosis["attention_bias_clue"],
            "behavior": diagnosis["behavior_pattern_clue"],
            "result": "Income stays constrained or unstable.",
            "reinforcement": diagnosis["reinforcement_logic"],
        }

    def _generate_restructuring(
        self,
        diagnosis: dict[str, Any],
        old_cycle_map: dict[str, Any],
        dna: dict[str, Any] | None,
    ) -> dict[str, Any]:
        mechanism = diagnosis["leading_mechanism_hypothesis"]
        if mechanism == "money_through_strain":
            new_belief = "Income can move through clearer value and cleaner asks, not only through more strain."
            attention = "Notice where value already exists but is not being claimed."
            behavior = "Make one cleaner ask before adding more effort."
            result = "One concrete moment of claiming value more directly."
            reinforcement = "A cleaner move can create traction without overload."
        elif mechanism == "underpricing_visibility_avoidance":
            new_belief = "A clear ask can be safe and useful, even if not every ask converts."
            attention = "Notice where uncertainty is coming from unclear pricing rather than true rejection."
            behavior = "State one cleaner price or offer once."
            result = "One clearer pricing moment or ask."
            reinforcement = "Clarity can create signal even before a full yes."
        else:
            new_belief = "Small expansion can be safe enough to test."
            attention = "Notice one place where staying small is automatic rather than necessary."
            behavior = "Take one controlled expansion step."
            result = "One bounded act that stretches the old ceiling."
            reinforcement = "Expansion can stay contained and survivable."
        if dna and dna["phrasing_constraints"]:
            reinforcement = f"{reinforcement} Constraint kept: {dna['phrasing_constraints'][0]}."
        return {
            "artifact_id": f"restructure-{uuid4().hex[:10]}",
            "cycle_id": diagnosis["cycle_id"],
            "generated_at": self._now(),
            "new_belief": new_belief,
            "new_attention_target": attention,
            "new_behavior_direction": behavior,
            "desired_result_marker": result,
            "new_reinforcement_statement": reinforcement,
        }

    def _generate_action(self, restructuring: dict[str, Any]) -> dict[str, Any]:
        behavior = restructuring["new_behavior_direction"].lower()
        if "ask" in behavior or "price" in behavior:
            action = "Send one clear money-related ask or price statement without extra apology."
            criterion = "One specific message, proposal, or spoken ask is delivered."
        elif "expansion" in behavior:
            action = "Make one bounded expansion move that was previously delayed by caution."
            criterion = "One concrete expansion step is completed and recorded."
        else:
            action = "Identify one place where value is already created and state it clearly once."
            criterion = "One value statement is made in writing or in conversation."
        return {
            "artifact_id": f"action-{uuid4().hex[:10]}",
            "cycle_id": restructuring["cycle_id"],
            "generated_at": self._now(),
            "action": action,
            "completion_criterion": criterion,
            "timeframe": "within 24 hours",
            "failure_risk_note": "The main risk is reverting to more effort or more explanation instead of a clean move.",
        }

    def _generate_progress_snapshot(
        self,
        record: dict[str, Any],
        checkin: dict[str, Any],
    ) -> dict[str, Any]:
        status = self._resolve_status(checkin)
        if status == "completed_shifted":
            shift = "The user created evidence that the replacement cycle can hold."
            barrier = "Keep the next cycle narrow so the shift becomes repeatable."
        elif status == "completed_partial":
            shift = "There was movement, but the replacement cycle is not yet stable."
            barrier = "The old cycle still competes with the new one."
        else:
            shift = "No meaningful shift marker was established."
            barrier = "The old cycle remained dominant during the action attempt."
        return {
            "artifact_id": f"progress-{uuid4().hex[:10]}",
            "cycle_id": record["cycle_id"],
            "recorded_at": self._now(),
            "resolution_status": status,
            "shift_marker": shift,
            "remaining_barrier": barrier,
            "memory_update_note": "Cycle result stored for later continuity.",
        }

    def _resolve_status(self, checkin: dict[str, Any]) -> str:
        combined = " ".join(
            [
                checkin["completion_status"],
                checkin["observed_external_result"],
                checkin["observed_internal_reaction"],
                checkin["old_cycle_return_note"],
            ]
        ).lower()
        positive_tokens = (
            "sent",
            "asked",
            "raised",
            "clear",
            "client",
            "reply",
            "payment",
            "calmer",
            "confidence",
            "easier",
            "pricing",
        )
        if checkin["completion_status"] == "completed" and any(token in combined for token in positive_tokens):
            return "completed_shifted"
        if checkin["completion_status"] in {"completed", "partial"}:
            return "completed_partial"
        return "completed_blocked"

    def _update_memory_record(self, record: dict[str, Any]) -> None:
        memory = self.store.load_or_create_memory_record(record["user_id"])
        memory["cycle_count"] += 1
        mechanism = record["diagnosis_output"]["leading_mechanism_hypothesis"]
        memory["last_mechanism_label"] = mechanism
        if mechanism not in memory["repeated_mechanism_markers"]:
            memory["repeated_mechanism_markers"].append(mechanism)
        barrier = record["progress_snapshot"]["remaining_barrier"]
        if barrier not in memory["repeated_barrier_markers"]:
            memory["repeated_barrier_markers"].append(barrier)
        memory["shift_history"].append(
            {
                "cycle_id": record["cycle_id"],
                "resolution_status": record["resolution_status"],
                "shift_marker": record["progress_snapshot"]["shift_marker"],
            }
        )
        memory["last_resolution_status"] = record["resolution_status"]
        memory["updated_at"] = self._now()
        self.store.save_memory_record(memory)

    def _save(self, record: dict[str, Any]) -> None:
        record["updated_at"] = self._now()
        self.store.save_cycle_record(record)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
