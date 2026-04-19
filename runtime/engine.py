from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from runtime.meaning import CompositeMeaningGenerator, build_default_meaning_generator
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

CANONICAL_MECHANISMS = {
    "money_through_strain",
    "underpricing_visibility_avoidance",
    "free_value_leakage",
    "deferred_money_conversation",
    "value_discount_when_easy",
    "rejection_collapse_pricing",
    "sales_avoidance_preparation_loop",
    "safety_in_smallness",
}


class GuardrailError(ValueError):
    """Raised when the accepted flow or guardrails would be violated."""


@dataclass
class CycleEngine:
    store: LocalJsonStore
    meaning_generator: CompositeMeaningGenerator = field(default_factory=build_default_meaning_generator)

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
            raise GuardrailError("Нужны описание проблемы и повторяющегося паттерна.")
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
            raise GuardrailError("Нельзя строить диагноз без полного Intake Record.")
        dna = self._generate_dna_support(intake)
        diagnosis_data = self.meaning_generator.diagnosis(intake, dna)
        try:
            diagnosis = self._validate_diagnosis_output(cycle_id, diagnosis_data)
        except GuardrailError:
            diagnosis = self._validate_with_fallback(
                cycle_id,
                lambda generator: generator.diagnosis(intake, dna),
                self._validate_diagnosis_output,
            )
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
            raise GuardrailError("Нужны Diagnosis Output и Old Cycle Map перед перестройкой.")
        restructuring_data = self.meaning_generator.restructuring(diagnosis, old_cycle, record["dna_support_signals"])
        try:
            restructuring = self._validate_restructuring_output(cycle_id, restructuring_data)
        except GuardrailError:
            restructuring = self._validate_with_fallback(
                cycle_id,
                lambda generator: generator.restructuring(diagnosis, old_cycle, record["dna_support_signals"]),
                self._validate_restructuring_output,
            )
        record["restructuring_output"] = restructuring
        self._transition_process_state(record, "restructured")
        self._save(record)
        return record

    def assign_action(self, cycle_id: str) -> dict[str, Any]:
        record = self.store.load_cycle_record(cycle_id)
        self._require_state(record, "restructured")
        if record["action_output"] is not None:
            raise GuardrailError("Для цикла уже существует Action Output.")
        restructuring = record["restructuring_output"]
        if not restructuring:
            raise GuardrailError("Нужен Restructuring Output перед назначением действия.")
        action_data = self.meaning_generator.action(restructuring)
        try:
            action = self._validate_action_output(cycle_id, action_data)
        except GuardrailError:
            action = self._validate_with_fallback(
                cycle_id,
                lambda generator: generator.action(restructuring),
                self._validate_action_output,
            )
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
            raise GuardrailError("Неожиданный статус выполнения check-in.")
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
        resolution_status = self._resolve_status(checkin)
        progress_data = self.meaning_generator.progress(record, checkin, resolution_status)
        try:
            progress = self._validate_progress_snapshot(cycle_id, resolution_status, progress_data)
        except GuardrailError:
            progress = self._validate_with_fallback(
                cycle_id,
                lambda generator: generator.progress(record, checkin, resolution_status),
                lambda fallback_cycle_id, data: self._validate_progress_snapshot(
                    fallback_cycle_id,
                    resolution_status,
                    data,
                ),
            )
        record["progress_snapshot"] = progress
        record["resolution_status"] = resolution_status
        self._transition_process_state(record, "cycle_resolved")
        self._update_memory_record(record)
        self._save(record)
        return record

    def _validate_diagnosis_output(self, cycle_id: str, data: dict[str, Any]) -> dict[str, Any]:
        required = [
            "leading_mechanism_hypothesis",
            "old_belief_statement",
            "attention_bias_clue",
            "behavior_pattern_clue",
            "reinforcement_logic",
            "hidden_prohibition_statement",
            "diagnosis_confidence_note",
        ]
        validated = self._validate_string_fields(data, required, "Diagnosis Output")
        if validated["leading_mechanism_hypothesis"] not in CANONICAL_MECHANISMS:
            raise GuardrailError("Diagnosis Output должен использовать один канонический label механизма.")
        return {
            "artifact_id": f"diagnosis-{uuid4().hex[:10]}",
            "cycle_id": cycle_id,
            "generated_at": self._now(),
            **validated,
        }

    def _validate_restructuring_output(self, cycle_id: str, data: dict[str, Any]) -> dict[str, Any]:
        required = [
            "new_belief",
            "new_attention_target",
            "new_behavior_direction",
            "desired_result_marker",
            "new_reinforcement_statement",
        ]
        validated = self._validate_string_fields(data, required, "Restructuring Output")
        return {
            "artifact_id": f"restructure-{uuid4().hex[:10]}",
            "cycle_id": cycle_id,
            "generated_at": self._now(),
            **validated,
        }

    def _validate_action_output(self, cycle_id: str, data: dict[str, Any]) -> dict[str, Any]:
        required = [
            "action",
            "completion_criterion",
            "timeframe",
            "failure_risk_note",
        ]
        validated = self._validate_string_fields(data, required, "Action Output")
        self._enforce_action_quality(validated["action"], validated["completion_criterion"])
        return {
            "artifact_id": f"action-{uuid4().hex[:10]}",
            "cycle_id": cycle_id,
            "generated_at": self._now(),
            **validated,
        }

    def _validate_progress_snapshot(
        self,
        cycle_id: str,
        resolution_status: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        required = ["shift_marker", "remaining_barrier", "memory_update_note"]
        validated = self._validate_string_fields(data, required, "Progress Snapshot")
        return {
            "artifact_id": f"progress-{uuid4().hex[:10]}",
            "cycle_id": cycle_id,
            "recorded_at": self._now(),
            "resolution_status": resolution_status,
            **validated,
        }

    def _validate_string_fields(
        self,
        data: dict[str, Any],
        required: list[str],
        artifact_name: str,
    ) -> dict[str, str]:
        if not isinstance(data, dict):
            raise GuardrailError(f"{artifact_name} должен быть объектом.")
        validated: dict[str, str] = {}
        for key in required:
            value = data.get(key)
            if not isinstance(value, str) or not value.strip():
                raise GuardrailError(f"{artifact_name} содержит некорректное поле {key}.")
            validated[key] = value.strip()
        return validated

    def _validate_with_fallback(self, cycle_id: str, fallback_call, validator):
        fallback_generator = getattr(self.meaning_generator, "fallback", None)
        if fallback_generator is None:
            raise GuardrailError("LLM-вывод не прошёл валидацию и fallback недоступен.")
        fallback_data = fallback_call(fallback_generator)
        return validator(cycle_id, fallback_data)

    def _enforce_action_quality(self, action: str, criterion: str) -> None:
        action_lower = action.lower()
        criterion_lower = criterion.lower()
        forbidden_starts = ("осознай", "подумай", "проанализируй", "начни относиться", "понаблюдай")
        if action_lower.startswith(forbidden_starts):
            raise GuardrailError("Action Output слишком расплывчатый и не задаёт проверяемый внешний шаг.")
        if any(marker in action_lower for marker in ("\n", ";", "1.", "2.", "•")):
            raise GuardrailError("Action Output не должен превращаться в список или многошаговый план.")
        if any(token in action_lower for token in ("два ", "две ", "три ", "трех", "трёх", "несколько ", "вариант", "способы", "список")):
            raise GuardrailError("Action Output не должен расширяться в несколько шагов или вариантов.")
        if len(action.strip()) < 25 or len(criterion.strip()) < 25:
            raise GuardrailError("Action Output слишком короткий и, вероятно, недостаточно конкретный.")
        drift_markers = ("изуч", "исслед", "инвест", "курс", "платформ", "зарегистр", "составь план", "план диалога", "составить список", "начать искать")
        if any(marker in action_lower for marker in drift_markers):
            raise GuardrailError("Action Output ушёл в подготовку, исследование или внешний сценарный drift.")
        alternative_markers = (
            " или назови",
            " или сделай",
            " или отправь",
            " или выбери",
            " или напиши",
            " или инициируй",
        )
        if any(marker in action_lower for marker in alternative_markers):
            raise GuardrailError("Action Output не должен предлагать несколько альтернативных действий.")
        outcome_markers = (
            "получение",
            "получил",
            "получена",
            "положительн",
            "увеличение дохода",
            "доход начинает",
            "доход увелич",
            "успешно получил",
        )
        if any(marker in criterion_lower for marker in outcome_markers):
            raise GuardrailError("Completion criterion не должен зависеть от внешнего исхода вместо завершения действия.")
        if not any(token in criterion_lower for token in ("один", "одна", "одно", "отправ", "назван", "инициирован", "выполнен", "озвучен")):
            raise GuardrailError("Completion criterion должен быть проверяемым и привязанным к одному действию.")

    def _transition_process_state(self, record: dict[str, Any], new_state: str) -> None:
        current = record["process_state"]
        if new_state not in PROCESS_STATES:
            raise GuardrailError(f"Неизвестное состояние процесса: {new_state}")
        if new_state not in ALLOWED_TRANSITIONS[current]:
            raise GuardrailError(f"Недопустимый переход состояния: {current} -> {new_state}")
        if new_state == "diagnosed" and (record["diagnosis_output"] is None or record["old_cycle_map"] is None):
            raise GuardrailError("Нельзя перейти в diagnosed без Diagnosis Output и Old Cycle Map.")
        if new_state == "restructured" and record["restructuring_output"] is None:
            raise GuardrailError("Нельзя перейти в restructured без Restructuring Output.")
        if new_state == "action_assigned" and record["action_output"] is None:
            raise GuardrailError("Нельзя перейти в action_assigned без Action Output.")
        if new_state == "checkin_received" and record["checkin_output"] is None:
            raise GuardrailError("Нельзя перейти в checkin_received без Check-In Output.")
        if new_state == "cycle_resolved":
            if record["progress_snapshot"] is None:
                raise GuardrailError("Нельзя завершить цикл без Progress Snapshot.")
            if record["resolution_status"] not in RESOLUTION_STATUSES - {"none"}:
                raise GuardrailError("Нельзя завершить цикл со статусом resolution_status=none.")
        record["process_state"] = new_state
        record["updated_at"] = self._now()

    def _require_state(self, record: dict[str, Any], expected: str) -> None:
        if record["process_state"] != expected:
            raise GuardrailError(f"Ожидалось состояние {expected}, получено {record['process_state']}.")

    def _extract_candidate_beliefs(self, problem_summary: str, repeated_pattern_summary: str) -> list[str]:
        text = f"{problem_summary} {repeated_pattern_summary}".lower()
        beliefs: list[str] = []
        if any(token in text for token in ("тяж", "впах", "много работ", "паш")):
            beliefs.append("деньги приходят только через тяжёлое усилие")
        if any(token in text for token in ("цен", "стоим", "прос", "откаж", "прода")):
            beliefs.append("просить больше денег рискованно")
        if not beliefs:
            beliefs.append("оставаться маленьким безопаснее, чем реально расширяться")
        return beliefs[:1]

    def _extract_behavior_clues(self, problem_summary: str, repeated_pattern_summary: str) -> list[str]:
        text = f"{problem_summary} {repeated_pattern_summary}".lower()
        clues: list[str] = []
        if any(token in text for token in ("работ", "впах", "паш", "выгора", "усили")):
            clues.append("добавляет усилие вместо смены способа получения результата")
        if any(token in text for token in ("цен", "прос", "оффер", "предлож", "прода")):
            clues.append("смягчает цену или избегает прямого денежного запроса")
        if self._has_affirmed_free_value_phase(text):
            clues.append("сначала даёт ценность, а платный переход обозначает слишком поздно")
        if any(token in text for token in ("отклады", "надо еще", "надо ещё", "доказать ценность", "пересмотр", "компенсац", "зарплат")):
            clues.append("откладывает денежный разговор под видом дополнительного доказательства ценности")
        if not clues:
            clues.append("удерживает знакомый низкий потолок как будто он безопаснее")
        return clues[:2]

    def _generate_dna_support(self, intake: dict[str, Any]) -> dict[str, Any]:
        text = f"{intake['problem_summary']} {intake['repeated_pattern_summary']}".lower()
        cues: list[str] = []
        prohibitions: list[str] = []
        resistance: list[str] = []
        phrasing: list[str] = []
        sabotage_point = "возврат к знакомому способу выживания вместо одного чистого шага"

        has_overload = self._has_any(text, "тяж", "впах", "паш", "выжива", "усили")
        has_price_tension = self._has_any(text, "цен", "прос", "откаж", "прода", "оффер", "деньг")
        has_free_value = self._has_affirmed_free_value_phase(text)
        has_paid_boundary = self._has_any(text, "платн", "оплат", "деньги", "стоимость", "предложени")
        has_delay = self._has_any(text, "отклады", "потом", "позже", "перенош", "не поднимал", "следующ")
        has_proof_loop = self._has_any(text, "доказать ценность", "надо еще", "надо ещё", "еще доказ", "ещё доказ", "сначала надо")
        has_compensation_context = self._has_any(text, "компенсац", "пересмотр", "повышен", "зарплат", "условий")
        has_soft_price = self._has_any(text, "смягча", "бонус", "не называ", "не наз", "мягко", "намека", "расплыв", "осторожно")

        if any(token in text for token in ("тяж", "впах", "паш", "выжива", "усили")):
            cues.append("язык перегруза и заслуживания")
            prohibitions.append("получать легче ощущается небезопасно")
            phrasing.append("не использовать обещания лёгких денег")
        if any(token in text for token in ("цен", "прос", "откаж", "прода", "оффер")):
            cues.append("напряжение вокруг запроса и цены")
            resistance.append("ясный запрос может активировать страх отказа")
            phrasing.append("говорить конкретно о ценности, а не общими лозунгами")
        if has_free_value and has_paid_boundary:
            cues.append("бесплатная польза растягивается раньше платной границы")
            prohibitions.append("ранний переход в деньги ощущается как риск разрушить контакт")
            resistance.append("момент платного перехода теряется после слишком длинной бесплатной помощи")
            phrasing.append("не смешивать поздний денежный разговор с утечкой ценности через бесплатность")
            sabotage_point = "снова дать ещё одну полезную бесплатную подсказку вместо платного следующего шага"
        if has_delay and (has_proof_loop or has_compensation_context):
            cues.append("денежный разговор переносится на потом под видом дополнительного доказательства ценности")
            prohibitions.append("о деньгах можно говорить только после ещё большего доказательства ценности")
            resistance.append("подготовка и доказательство ценности заменяют сам денежный разговор")
            phrasing.append("не сводить откладывание денежного разговора к общей тревоге вокруг цены")
            sabotage_point = "снова решить, что сначала надо ещё доказать ценность, а потом уже говорить о деньгах"
        if has_free_value and has_delay:
            cues.append("платный переход запаздывает: бесплатная отдача и перенос разговора о деньгах накладываются друг на друга")
            cues.append("первичный сбой происходит в точке платной границы уже после бесплатно отданной ценности")
            resistance.append("после бесплатной пользы разговор о деньгах переносится, как будто право на платный шаг ещё не возникло")
            phrasing.append("если delay возник уже после бесплатно отданной ценности, усиливать различение в сторону free_value_leakage, а не deferred_money_conversation")
            sabotage_point = "снова отдать ценность бесплатно и отложить платный переход ещё на один круг контакта"
        if has_free_value and has_soft_price:
            cues.append("после уже отданной бесплатно ценности цена смягчается слишком поздно вместо прямой платной границы")
            resistance.append("смягчённое называние цены происходит уже после утечки ценности в бесплатность")
            phrasing.append("если смягчённая цена появляется уже после бесплатной фазы, усиливать различение в сторону free_value_leakage, а не underpricing_visibility_avoidance")
            sabotage_point = "снова смягчить поздний денежный переход вместо того, чтобы вовремя обозначить платный шаг"
        if has_soft_price and not has_free_value:
            cues.append("первичный сбой находится в прямом назывании цены, а не в утечке ценности в бесплатность")
            resistance.append("цена смягчается или размывается без выраженной бесплатной фазы до этого")
            phrasing.append("не относить кейс к free_value_leakage без явной бесплатной фазы до денежного перехода")
        if not cues:
            cues.append("язык удержания маленького масштаба")
            prohibitions.append("рост может ощущаться как риск потери устойчивости")
            phrasing.append("держать перестройку постепенной")
        return {
            "artifact_id": f"dna-{uuid4().hex[:10]}",
            "cycle_id": intake["cycle_id"],
            "generated_at": self._now(),
            "hidden_structure_cues": cues[:4],
            "prohibition_signals": prohibitions[:1],
            "resistance_pattern_notes": resistance[:2] or ["базовое сопротивление: возврат к привычному низкому потолку"],
            "likely_self_sabotage_point": sabotage_point,
            "phrasing_constraints": phrasing[:3],
        }

    def _has_any(self, text: str, *tokens: str) -> bool:
        return any(token in text for token in tokens)

    def _has_affirmed_free_value_phase(self, text: str) -> bool:
        has_free_value_signal = self._has_any(
            text,
            "бесплат",
            "до оплат",
            "до сделки",
            "разбор",
            "консульт",
            "совет",
            "даю решение",
            "много помогаю",
            "полезн",
        )
        has_negated_free_value = self._has_any(
            text,
            "не отдаю бесплатно",
            "не отдавал бесплатно",
            "не даю бесплатно",
            "не было бесплат",
            "без бесплат",
            "не отдаю ценность",
            "бесплатную ценность заранее не отдаю",
        )
        return has_free_value_signal and not has_negated_free_value

    def _generate_old_cycle_map(self, diagnosis: dict[str, Any]) -> dict[str, Any]:
        result_by_mechanism = {
            "money_through_strain": "Доход остаётся ограниченным, потому что рост всё время пытаются купить только дополнительным напряжением.",
            "underpricing_visibility_avoidance": "Доход остаётся слабым, потому что ясный запрос или цена так и не предъявляются прямо.",
            "safety_in_smallness": "Доход остаётся в знакомом потолке, потому что любое расширение быстро сворачивается назад.",
        }
        return {
            "artifact_id": f"old-cycle-{uuid4().hex[:10]}",
            "cycle_id": diagnosis["cycle_id"],
            "mapped_at": self._now(),
            "belief": diagnosis["old_belief_statement"],
            "attention": diagnosis["attention_bias_clue"],
            "behavior": diagnosis["behavior_pattern_clue"],
            "result": result_by_mechanism.get(
                diagnosis["leading_mechanism_hypothesis"],
                "Доход остаётся ограниченным и повторяет старую схему.",
            ),
            "reinforcement": diagnosis["reinforcement_logic"],
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
            "отправ",
            "сказал",
            "назвал",
            "ответ",
            "оплат",
            "спокой",
            "уверен",
            "легче",
            "ясн",
            "цен",
            "запрос",
            "оффер",
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
