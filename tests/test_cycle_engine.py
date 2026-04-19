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


class NonCanonicalDiagnosisGenerator(StubMeaningGenerator):
    def diagnosis(self, intake, dna):
        result = super().diagnosis(intake, dna)
        result["leading_mechanism_hypothesis"] = "Страх отказа мешает говорить о цене прямо."
        return result


class InvalidActionGenerator(StubMeaningGenerator):
    def action(self, restructuring):
        result = super().action(restructuring)
        result["action"] = ["сделай это", "и это тоже"]
        return result


class OutcomeBasedActionGenerator(StubMeaningGenerator):
    def action(self, restructuring):
        return {
            "action": "Запрашивать цену выше на свои услуги.",
            "completion_criterion": "Получение положительного отклика от клиента на новое предложение.",
            "timeframe": "в течение недели",
            "failure_risk_note": "Риск - тревога перед реакцией клиента.",
        }


class DriftActionGenerator(StubMeaningGenerator):
    def action(self, restructuring):
        return {
            "action": "Изучить три новых способа инвестирования, используя онлайн-ресурсы или курсы.",
            "completion_criterion": "Один новый вариант записан и первые шаги к его реализации начаты.",
            "timeframe": "в течение недели",
            "failure_risk_note": "Риск - распылиться и не сделать реальный денежный шаг.",
        }


class TerseActionGenerator(StubMeaningGenerator):
    def action(self, restructuring):
        return {
            "action": "Сформулировать и озвучить один чёткий финансовый запрос.",
            "completion_criterion": "Один запрос озвучен.",
            "timeframe": "в течение 24 часов",
            "failure_risk_note": "Риск - снова смягчить формулировку.",
        }


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

    def _build_intake(self, problem_summary: str, repeated_pattern_summary: str, desired_shift: str = "") -> dict:
        return {
            "artifact_id": "intake-test",
            "cycle_id": "cycle-test",
            "captured_at": self.engine._now(),
            "problem_summary": problem_summary,
            "repeated_pattern_summary": repeated_pattern_summary,
            "candidate_belief_language": self.engine._extract_candidate_beliefs(problem_summary, repeated_pattern_summary),
            "candidate_behavior_clues": self.engine._extract_behavior_clues(problem_summary, repeated_pattern_summary),
            "intake_completeness_flag": True,
            "source_excerpt": desired_shift,
        }

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

    def test_noncanonical_mechanism_label_falls_back(self) -> None:
        engine = self._engine_with_generator(NonCanonicalDiagnosisGenerator())
        cycle = engine.create_cycle(
            problem_summary="Я боюсь прямо назвать цену.",
            repeated_pattern_summary="Каждый раз смягчаю оффер и ухожу в оправдания.",
            desired_shift="Хочу один прямой денежный шаг.",
        )
        self.assertIn(
            cycle["diagnosis_output"]["leading_mechanism_hypothesis"],
            {
                "money_through_strain",
                "underpricing_visibility_avoidance",
                "free_value_leakage",
                "deferred_money_conversation",
                "value_discount_when_easy",
                "rejection_collapse_pricing",
                "sales_avoidance_preparation_loop",
                "safety_in_smallness",
            },
        )

    def test_dna_support_marks_free_value_leakage_boundary(self) -> None:
        intake = self._build_intake(
            problem_summary="Люди часто просят у меня совет по маркетингу, я много помогаю бесплатно, а потом остаюсь без продаж.",
            repeated_pattern_summary="Мне неудобно быстро переводить разговор в деньги, поэтому я сначала отдаю много ценности, а потом теряю момент.",
            desired_shift="Хочу раньше обозначать платный формат.",
        )
        dna = self.engine._generate_dna_support(intake)
        combined = " ".join(
            dna["hidden_structure_cues"] + dna["resistance_pattern_notes"] + dna["phrasing_constraints"] + [dna["likely_self_sabotage_point"]]
        ).lower()
        self.assertIn("бесплат", combined)
        self.assertTrue(any(token in combined for token in ("платн", "оплат", "границ")))

    def test_dna_support_marks_deferred_money_conversation_boundary(self) -> None:
        intake = self._build_intake(
            problem_summary="Я тяну больше ответственности в компании, но уже давно не поднимал вопрос о компенсации.",
            repeated_pattern_summary="Каждый раз думаю, что надо еще немного доказать ценность, и откладываю разговор о деньгах.",
            desired_shift="Хочу подготовить один ясный разговор о пересмотре дохода.",
        )
        dna = self.engine._generate_dna_support(intake)
        combined = " ".join(
            dna["hidden_structure_cues"] + dna["prohibition_signals"] + dna["resistance_pattern_notes"] + dna["phrasing_constraints"] + [dna["likely_self_sabotage_point"]]
        ).lower()
        self.assertTrue(any(token in combined for token in ("доказ", "компенсац", "разговор")))
        self.assertTrue(any(token in combined for token in ("отклады", "потом", "перенос")))

    def test_dna_support_overlap_case_marks_free_and_delay_together(self) -> None:
        intake = self._build_intake(
            problem_summary="Я много помогаю потенциальным клиентам до сделки и часто даю подробные разборы бесплатно.",
            repeated_pattern_summary="Потом говорю себе, что сначала надо еще сильнее показать ценность, и откладываю переход к платному предложению.",
            desired_shift="Хочу раньше переводить разговор в платный шаг.",
        )
        dna = self.engine._generate_dna_support(intake)
        combined = " ".join(
            dna["hidden_structure_cues"] + dna["resistance_pattern_notes"] + dna["phrasing_constraints"] + [dna["likely_self_sabotage_point"]]
        ).lower()
        self.assertIn("бесплат", combined)
        self.assertTrue(any(token in combined for token in ("платн", "разговор", "доказ")))

    def test_dna_support_marks_late_soft_price_after_free_help_as_boundary_failure(self) -> None:
        intake = self._build_intake(
            problem_summary="Я сначала подробно помогаю клиенту бесплатно, чтобы показать пользу.",
            repeated_pattern_summary="Когда потом доходит до оплаты, я не называю цену прямо, а мягко намекаю на платный пакет и снова размываю границу.",
            desired_shift="Хочу не терять платную границу после уже отданной ценности.",
        )
        dna = self.engine._generate_dna_support(intake)
        combined = " ".join(
            dna["hidden_structure_cues"] + dna["resistance_pattern_notes"] + dna["phrasing_constraints"] + [dna["likely_self_sabotage_point"]]
        ).lower()
        self.assertIn("бесплат", combined)
        self.assertTrue(any(token in combined for token in ("смягч", "размыв", "границ", "платн")))

    def test_dna_support_does_not_fake_free_value_when_user_denies_it(self) -> None:
        intake = self._build_intake(
            problem_summary="Я почти сразу дохожу до обсуждения работы с клиентом, но мне трудно назвать сумму прямо.",
            repeated_pattern_summary="Я смягчаю оффер, добавляю бонусы и боюсь уверенно назвать цену, хотя бесплатную ценность заранее не отдаю.",
            desired_shift="Хочу говорить цену прямее без смягчения.",
        )
        dna = self.engine._generate_dna_support(intake)
        combined = " ".join(
            dna["hidden_structure_cues"] + dna["resistance_pattern_notes"] + dna["phrasing_constraints"] + [dna["likely_self_sabotage_point"]]
        ).lower()
        self.assertTrue(any(token in combined for token in ("цен", "сумм", "оффер", "смягч", "прям")))
        self.assertNotIn("бесплатная польза растягивается раньше платной границы", combined)

    def test_stub_llm_can_drive_full_cycle(self) -> None:
        engine = self._engine_with_generator(StubMeaningGenerator())
        cycle = engine.create_cycle(
            problem_summary="Я боюсь просить деньги.",
            repeated_pattern_summary="Каждый раз ухожу в лишние объяснения.",
            desired_shift="Хочу сделать один ясный запрос.",
        )
        self.assertEqual(cycle["diagnosis_output"]["diagnosis_confidence_note"], "Тестовый LLM-ответ.")
        self.assertEqual(cycle["action_output"]["action"], "Один раз прямо назвать цену или запрос.")

    def test_real_case_quality_harness(self) -> None:
        cases = [
            {
                "name": "Фрилансер боится поднять цену",
                "problem": "Я делаю сайты на фрилансе, но уже год беру почти те же деньги и злюсь на себя за это.",
                "pattern": "Когда доходит до цены, я начинаю смягчать оффер, добавлять бонусы и боюсь назвать сумму прямо.",
                "shift": "Хочу научиться говорить цену спокойнее и прямее.",
                "mechanism": "underpricing_visibility_avoidance",
                "action_contains": "назови цену",
            },
            {
                "name": "Перегруженный специалист",
                "problem": "Я много работаю, беру дополнительные задачи, но доход растет очень медленно.",
                "pattern": "Каждый раз думаю, что нужно просто еще сильнее впахивать, и почти не смотрю на другие способы роста.",
                "shift": "Хочу перестать покупать деньги только усталостью.",
                "mechanism": "money_through_strain",
                "action_contains": "денежный запрос",
            },
            {
                "name": "Эксперт с бесплатными консультациями",
                "problem": "Люди часто просят у меня совет по маркетингу, я много помогаю бесплатно, а потом остаюсь без продаж.",
                "pattern": "Мне неудобно быстро переводить разговор в деньги, поэтому я сначала отдаю много ценности, а потом теряю момент.",
                "shift": "Хочу раньше обозначать платный формат.",
                "mechanism": "free_value_leakage",
                "action_contains": "платный",
            },
            {
                "name": "Руководитель не просит повышение",
                "problem": "Я тяну больше ответственности в компании, но уже давно не поднимал вопрос о компенсации.",
                "pattern": "Каждый раз думаю, что надо еще немного доказать ценность, и откладываю разговор о деньгах.",
                "shift": "Хочу подготовить один ясный разговор о пересмотре дохода.",
                "mechanism": "deferred_money_conversation",
                "action_contains": "разговор",
            },
            {
                "name": "Предприниматель держится за маленький потолок",
                "problem": "У меня есть небольшой стабильный доход, но как только появляется шанс расшириться, я сам себя торможу.",
                "pattern": "Я выбираю безопасные маленькие действия и откладываю шаги, которые могут реально увеличить масштаб.",
                "shift": "Хочу выдержать маленькое, но реальное расширение.",
                "mechanism": "safety_in_smallness",
                "action_contains": "расширение",
            },
            {
                "name": "Специалист боится продаж",
                "problem": "Я хороший специалист, но от самой мысли о продажах и прямых предложениях меня сжимает.",
                "pattern": "Я долго готовлюсь, улучшаю продукт, но избегаю напрямую писать потенциальным клиентам.",
                "shift": "Хочу сделать один прямой оффер без долгой подготовки.",
                "mechanism": "sales_avoidance_preparation_loop",
                "action_contains": "оффер",
            },
            {
                "name": "Эксперт путает ценность и тяжесть",
                "problem": "Мне трудно брать хорошие деньги, если задача кажется слишком легкой для меня.",
                "pattern": "Если я делаю что-то быстро, у меня включается мысль, что за это нельзя просить серьезную сумму.",
                "shift": "Хочу отделить ценность результата от тяжести процесса.",
                "mechanism": "value_discount_when_easy",
                "action_contains": "результат",
            },
            {
                "name": "Страх отказа после одного нет",
                "problem": "После нескольких отказов мне кажется, что рынок не готов платить мне больше.",
                "pattern": "Я начинаю занижать цену после первого же холодного ответа и воспринимаю это как знак не лезть выше.",
                "shift": "Хочу выдерживать отказ без автоматического снижения цены.",
                "mechanism": "rejection_collapse_pricing",
                "action_contains": "отказа",
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                cycle = self.engine.create_cycle(
                    problem_summary=case["problem"],
                    repeated_pattern_summary=case["pattern"],
                    desired_shift=case["shift"],
                )
                self.assertEqual(
                    cycle["diagnosis_output"]["leading_mechanism_hypothesis"],
                    case["mechanism"],
                )
                self.assertIn(case["action_contains"], cycle["action_output"]["action"].lower())

    def test_rejects_vague_action_output(self) -> None:
        class VagueActionGenerator(StubMeaningGenerator):
            def action(self, restructuring):
                return {
                    "action": "Осознай свой страх и подумай о деньгах иначе.",
                    "completion_criterion": "Пойми, что ты готов к новому уровню.",
                    "timeframe": "сегодня",
                    "failure_risk_note": "Риск - сомневаться.",
                }

        engine = self._engine_with_generator(VagueActionGenerator())
        cycle = engine.create_cycle(
            problem_summary="Я боюсь называть деньги.",
            repeated_pattern_summary="Я снова ухожу в общие размышления вместо конкретного запроса.",
            desired_shift="Хочу один внешний шаг.",
        )
        self.assertNotIn("осознай", cycle["action_output"]["action"].lower())
        self.assertTrue(
            any(
                token in cycle["action_output"]["completion_criterion"].lower()
                for token in ("один", "одна", "запрос", "цена", "отправ")
            )
        )

    def test_rejects_outcome_based_completion_criterion(self) -> None:
        engine = self._engine_with_generator(OutcomeBasedActionGenerator())
        cycle = engine.create_cycle(
            problem_summary="Я боюсь повысить цену.",
            repeated_pattern_summary="Мне кажется, что всё зависит от реакции клиента.",
            desired_shift="Хочу один ясный внешний шаг.",
        )
        self.assertNotIn("получение положительного отклика", cycle["action_output"]["completion_criterion"].lower())
        self.assertTrue(
            any(
                token in cycle["action_output"]["completion_criterion"].lower()
                for token in ("один", "одна", "назван", "отправ", "инициирован", "выполнен", "озвучен")
            )
        )

    def test_rejects_action_drift_into_research_or_investing(self) -> None:
        engine = self._engine_with_generator(DriftActionGenerator())
        cycle = engine.create_cycle(
            problem_summary="Я много работаю, но не делаю более ясных денежных шагов.",
            repeated_pattern_summary="Я ухожу в новые идеи вместо одного прямого запроса.",
            desired_shift="Хочу один узкий денежный шаг.",
        )
        self.assertNotIn("инвест", cycle["action_output"]["action"].lower())
        self.assertNotIn("изуч", cycle["action_output"]["action"].lower())

    def test_rejects_terse_completion_criterion(self) -> None:
        engine = self._engine_with_generator(TerseActionGenerator())
        cycle = engine.create_cycle(
            problem_summary="Я работаю слишком много и избегаю прямых денег.",
            repeated_pattern_summary="Я хочу назвать сумму, но снова всё смягчаю.",
            desired_shift="Хочу один ясный внешний шаг.",
        )
        self.assertNotEqual(cycle["action_output"]["completion_criterion"], "Один запрос озвучен.")
        self.assertTrue(
            any(
                token in cycle["action_output"]["completion_criterion"].lower()
                for token in ("один", "одна", "отправ", "назван", "инициирован", "выполнен", "озвучен")
            )
        )

    def test_overlap_case_prefers_free_value_leakage_over_generic_delay(self) -> None:
        cycle = self.engine.create_cycle(
            problem_summary="Я много помогаю потенциальным клиентам до сделки и часто даю подробные разборы бесплатно.",
            repeated_pattern_summary="Потом говорю себе, что сначала надо еще сильнее показать ценность, и откладываю переход к платному предложению.",
            desired_shift="Хочу раньше переводить разговор в платный шаг.",
        )
        self.assertEqual(cycle["diagnosis_output"]["leading_mechanism_hypothesis"], "free_value_leakage")

    def test_free_help_then_soft_price_prefers_free_value_leakage(self) -> None:
        cycle = self.engine.create_cycle(
            problem_summary="Я сначала подробно помогаю клиенту бесплатно, чтобы показать пользу.",
            repeated_pattern_summary="Когда потом доходит до оплаты, я не называю цену прямо, а мягко намекаю на платный пакет и снова размываю границу.",
            desired_shift="Хочу не терять платную границу после уже отданной ценности.",
        )
        self.assertEqual(cycle["diagnosis_output"]["leading_mechanism_hypothesis"], "free_value_leakage")

    def test_late_paid_boundary_after_free_help_prefers_free_value_leakage(self) -> None:
        cycle = self.engine.create_cycle(
            problem_summary="Я быстро вхожу в помощь, разбираю ситуацию клиента и даю решения еще до оплаты.",
            repeated_pattern_summary="Потом мне кажется, что просить деньги уже неудобно, и я переношу разговор о платном формате на потом.",
            desired_shift="Хочу раньше обозначать границу между бесплатным контактом и оплатой.",
        )
        self.assertEqual(cycle["diagnosis_output"]["leading_mechanism_hypothesis"], "free_value_leakage")

    def test_pure_underpricing_without_leakage_stays_underpricing(self) -> None:
        cycle = self.engine.create_cycle(
            problem_summary="Я почти сразу дохожу до обсуждения работы с клиентом, но мне трудно назвать сумму прямо.",
            repeated_pattern_summary="Я смягчаю оффер, добавляю бонусы и боюсь уверенно назвать цену, хотя бесплатную ценность заранее не отдаю.",
            desired_shift="Хочу говорить цену прямее без смягчения.",
        )
        self.assertEqual(cycle["diagnosis_output"]["leading_mechanism_hypothesis"], "underpricing_visibility_avoidance")

    def test_free_value_leakage_without_price_fear_center_stays_free_value_leakage(self) -> None:
        cycle = self.engine.create_cycle(
            problem_summary="Я не так боюсь самих цифр, но к моменту разговора о деньгах уже успеваю бесплатно разобрать половину задачи клиента.",
            repeated_pattern_summary="Платный переход возникает слишком поздно, потому что основная ценность уже была отдана до оплаты.",
            desired_shift="Хочу раньше переводить контакт в платный следующий шаг.",
        )
        self.assertEqual(cycle["diagnosis_output"]["leading_mechanism_hypothesis"], "free_value_leakage")


if __name__ == "__main__":
    unittest.main()
