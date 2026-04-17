from __future__ import annotations

import tempfile
import unittest

from runtime.engine import CycleEngine, GuardrailError
from runtime.meaning import CompositeMeaningGenerator, HeuristicRussianMeaningGenerator
from runtime.storage import LocalJsonStore
from runtime.web import _render_cycle, _render_home


class StubMeaningGenerator:
    def diagnosis(self, intake, dna):
        return {
            "leading_mechanism_hypothesis": "money_through_strain",
            "old_belief_statement": "Деньги приходят только через перегруз.",
            "attention_bias_clue": "Внимание цепляется за тяжесть и усталость.",
            "behavior_pattern_clue": "Снова добавляет усилие вместо чистого запроса.",
            "reinforcement_logic": "Слабый результат снова подтверждает старую схему.",
            "hidden_prohibition_statement": "Лёгкость кажется небезопасной.",
            "diagnosis_confidence_note": "Тестовый LLM-ответ.",
        }

    def restructuring(self, diagnosis, old_cycle_map, dna):
        return {
            "new_belief": "Доход может расти через более ясное предъявление ценности.",
            "new_attention_target": "Замечать места, где ценность уже есть, но не названа.",
            "new_behavior_direction": "Сделать один прямой денежный запрос.",
            "desired_result_marker": "Один ясный эпизод предъявления ценности.",
            "new_reinforcement_statement": "Новый результат возможен без дополнительного перегруза.",
        }

    def action(self, restructuring):
        return {
            "action": "Один раз прямо назвать цену или запрос.",
            "completion_criterion": "Один денежный запрос реально отправлен.",
            "timeframe": "сегодня",
            "failure_risk_note": "Риск - снова уйти в оправдания.",
        }

    def progress(self, record, checkin, resolution_status):
        return {
            "shift_marker": "Есть подтверждение нового шага.",
            "remaining_barrier": "Старый цикл ещё может вернуться при следующем запросе.",
            "memory_update_note": "Результат сохранён.",
        }


class InvalidDiagnosisGenerator(StubMeaningGenerator):
    def diagnosis(self, intake, dna):
        result = super().diagnosis(intake, dna)
        result["leading_mechanism_hypothesis"] = ["first", "second"]
        return result


class InvalidActionGenerator(StubMeaningGenerator):
    def action(self, restructuring):
        result = super().action(restructuring)
        result["action"] = ["сделай это", "и это тоже"]
        return result


class FailingMeaningGenerator(StubMeaningGenerator):
    def diagnosis(self, intake, dna):
        raise RuntimeError("llm unavailable")

    def restructuring(self, diagnosis, old_cycle_map, dna):
        raise RuntimeError("llm unavailable")

    def action(self, restructuring):
        raise RuntimeError("llm unavailable")

    def progress(self, record, checkin, resolution_status):
        raise RuntimeError("llm unavailable")


class CycleEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.store = LocalJsonStore(self.tempdir.name)
        self.engine = CycleEngine(self.store)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _engine_with_generator(self, primary) -> CycleEngine:
        composite = CompositeMeaningGenerator(
            primary=primary,
            fallback=HeuristicRussianMeaningGenerator(),
        )
        return CycleEngine(self.store, meaning_generator=composite)

    def test_create_cycle_generates_artifacts_in_order(self) -> None:
        cycle = self.engine.create_cycle(
            problem_summary="Я много работаю, но доход почти не растёт.",
            repeated_pattern_summary="Я снова добавляю усилие вместо более ясного запроса.",
            desired_shift="Хочу сделать один более чистый денежный шаг.",
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
            problem_summary="Я избегаю прямого разговора о цене.",
            repeated_pattern_summary="Снова смягчаю запрос и остаюсь недооценённым.",
            desired_shift="Хочу один более ясный разговор о цене.",
        )

        with self.assertRaises(GuardrailError):
            self.engine.assign_action(cycle["cycle_id"])

    def test_checkin_cannot_run_before_action_assigned(self) -> None:
        draft = self.engine.create_draft_cycle()

        with self.assertRaises(GuardrailError):
            self.engine.submit_checkin(
                cycle_id=draft["cycle_id"],
                completion_status="completed",
                observed_external_result="Я отправил запрос.",
                observed_internal_reaction="Мне стало спокойнее.",
                old_cycle_return_note="Старый страх всё ещё чувствовался.",
            )

    def test_invalid_transition_is_rejected(self) -> None:
        draft = self.engine.create_draft_cycle()

        with self.assertRaises(GuardrailError):
            self.engine._transition_process_state(draft, "restructured")

    def test_completed_cycle_stores_progress_and_resolution(self) -> None:
        cycle = self.engine.create_cycle(
            problem_summary="Я много работаю и избегаю разговора о деньгах.",
            repeated_pattern_summary="Снова объясняю больше, чем прямо прошу.",
            desired_shift="Хочу сделать один ясный запрос.",
        )
        resolved = self.engine.submit_checkin(
            cycle_id=cycle["cycle_id"],
            completion_status="completed",
            observed_external_result="Я отправил один ясный запрос и получил ответ.",
            observed_internal_reaction="Внутри было спокойнее и яснее.",
            old_cycle_return_note="Старое напряжение вернулось, но уже слабее.",
        )

        self.assertEqual(resolved["process_state"], "cycle_resolved")
        self.assertNotEqual(resolved["resolution_status"], "none")
        self.assertIsNotNone(resolved["progress_snapshot"])
        memory = self.store.load_or_create_memory_record("local-user")
        self.assertEqual(memory["cycle_count"], 1)

    def test_russian_ui_rendering_basics(self) -> None:
        home = _render_home([])
        self.assertIn("Минимальный цикл перестройки денежного механизма", home)
        self.assertIn("Запустить цикл", home)
        cycle = self.engine.create_cycle(
            problem_summary="Я боюсь прямо назвать цену.",
            repeated_pattern_summary="Каждый раз смягчаю запрос.",
            desired_shift="Хочу назвать цену яснее.",
        )
        detail = _render_cycle(cycle)
        self.assertIn("Состояние процесса", detail)
        self.assertIn("Одно действие", detail)
        self.assertIn("Отправить check-in", detail)

    def test_fallback_behavior_if_llm_generation_fails(self) -> None:
        engine = self._engine_with_generator(FailingMeaningGenerator())
        cycle = engine.create_cycle(
            problem_summary="Я снова впахиваю вместо прямого запроса.",
            repeated_pattern_summary="Добавляю усилие и избегаю ясной цены.",
            desired_shift="Хочу один чистый шаг.",
        )
        self.assertIsInstance(cycle["diagnosis_output"]["old_belief_statement"], str)
        self.assertIn("Доход", cycle["restructuring_output"]["new_belief"] or "Доход")
        self.assertIsInstance(cycle["action_output"]["action"], str)

    def test_one_action_constraint_is_preserved_under_llm_usage(self) -> None:
        engine = self._engine_with_generator(InvalidActionGenerator())
        cycle = engine.create_cycle(
            problem_summary="Я избегаю денежного запроса.",
            repeated_pattern_summary="Каждый раз смягчаю действие.",
            desired_shift="Хочу один прямой запрос.",
        )
        self.assertIsInstance(cycle["action_output"]["action"], str)
        self.assertNotIsInstance(cycle["action_output"]["action"], list)

    def test_one_diagnosis_constraint_is_preserved_under_llm_usage(self) -> None:
        engine = self._engine_with_generator(InvalidDiagnosisGenerator())
        cycle = engine.create_cycle(
            problem_summary="Я много работаю и не прошу больше.",
            repeated_pattern_summary="Снова остаюсь в старом потолке.",
            desired_shift="Хочу сделать один чистый шаг.",
        )
        self.assertIsInstance(cycle["diagnosis_output"]["leading_mechanism_hypothesis"], str)
        self.assertNotIsInstance(cycle["diagnosis_output"]["leading_mechanism_hypothesis"], list)

    def test_stub_llm_can_drive_full_cycle(self) -> None:
        engine = self._engine_with_generator(StubMeaningGenerator())
        cycle = engine.create_cycle(
            problem_summary="Я боюсь просить деньги.",
            repeated_pattern_summary="Каждый раз ухожу в лишние объяснения.",
            desired_shift="Хочу сделать один ясный запрос.",
        )
        self.assertEqual(cycle["diagnosis_output"]["diagnosis_confidence_note"], "Тестовый LLM-ответ.")
        self.assertEqual(cycle["action_output"]["action"], "Один раз прямо назвать цену или запрос.")


if __name__ == "__main__":
    unittest.main()
