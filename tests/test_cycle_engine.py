from __future__ import annotations

import tempfile
import unittest

from runtime.engine import CycleEngine, GuardrailError
from runtime.storage import LocalJsonStore


class CycleEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.store = LocalJsonStore(self.tempdir.name)
        self.engine = CycleEngine(self.store)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_create_cycle_generates_artifacts_in_order(self) -> None:
        cycle = self.engine.create_cycle(
            problem_summary="I work a lot but income barely grows.",
            repeated_pattern_summary="I keep adding effort instead of making clearer asks.",
            desired_shift="I want a cleaner way to claim value.",
        )

        self.assertEqual(cycle["process_state"], "action_assigned")
        self.assertEqual(cycle["resolution_status"], "none")
        self.assertIsNotNone(cycle["intake_record"])
        self.assertIsNotNone(cycle["dna_support_signals"])
        self.assertIsNotNone(cycle["diagnosis_output"])
        self.assertIsNotNone(cycle["old_cycle_map"])
        self.assertIsNotNone(cycle["restructuring_output"])
        self.assertIsNotNone(cycle["action_output"])
        self.assertIsNone(cycle["checkin_output"])
        self.assertIsNone(cycle["progress_snapshot"])

    def test_assign_action_cannot_be_called_twice(self) -> None:
        cycle = self.engine.create_cycle(
            problem_summary="I avoid clean pricing.",
            repeated_pattern_summary="I keep softening asks and staying underpriced.",
            desired_shift="I want one cleaner price conversation.",
        )

        with self.assertRaises(GuardrailError):
            self.engine.assign_action(cycle["cycle_id"])

    def test_checkin_cannot_run_before_action_assigned(self) -> None:
        draft = self.engine.create_draft_cycle()

        with self.assertRaises(GuardrailError):
            self.engine.submit_checkin(
                cycle_id=draft["cycle_id"],
                completion_status="completed",
                observed_external_result="I sent the ask.",
                observed_internal_reaction="I was calmer than expected.",
                old_cycle_return_note="I still noticed the old fear.",
            )

    def test_invalid_transition_is_rejected(self) -> None:
        draft = self.engine.create_draft_cycle()

        with self.assertRaises(GuardrailError):
            self.engine._transition_process_state(draft, "restructured")

    def test_completed_cycle_stores_progress_and_resolution(self) -> None:
        cycle = self.engine.create_cycle(
            problem_summary="I work hard and avoid pricing conversations.",
            repeated_pattern_summary="I explain more instead of asking clearly.",
            desired_shift="I want to send one clear ask.",
        )
        resolved = self.engine.submit_checkin(
            cycle_id=cycle["cycle_id"],
            completion_status="completed",
            observed_external_result="I sent one clear ask and received a reply.",
            observed_internal_reaction="I felt calmer and more direct.",
            old_cycle_return_note="The old strain story showed up but did not stop me.",
        )

        self.assertEqual(resolved["process_state"], "cycle_resolved")
        self.assertNotEqual(resolved["resolution_status"], "none")
        self.assertIsNotNone(resolved["progress_snapshot"])
        memory = self.store.load_or_create_memory_record("local-user")
        self.assertEqual(memory["cycle_count"], 1)


if __name__ == "__main__":
    unittest.main()
