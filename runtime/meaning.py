from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib import error, request


class MeaningGenerationError(RuntimeError):
    """Raised when LLM-backed meaning generation is unavailable or invalid."""


def build_default_meaning_generator() -> "CompositeMeaningGenerator":
    return CompositeMeaningGenerator(
        primary=OpenAIResponsesMeaningGenerator.from_env(),
        fallback=HeuristicRussianMeaningGenerator(),
    )


@dataclass
class CompositeMeaningGenerator:
    primary: "MeaningGeneratorProtocol"
    fallback: "MeaningGeneratorProtocol"

    def diagnosis(self, intake: dict[str, Any], dna: dict[str, Any]) -> dict[str, str]:
        return self._call("diagnosis", intake, dna)

    def restructuring(
        self,
        diagnosis: dict[str, Any],
        old_cycle_map: dict[str, Any],
        dna: dict[str, Any] | None,
    ) -> dict[str, str]:
        return self._call("restructuring", diagnosis, old_cycle_map, dna)

    def action(self, restructuring: dict[str, Any]) -> dict[str, str]:
        return self._call("action", restructuring)

    def progress(
        self,
        record: dict[str, Any],
        checkin: dict[str, Any],
        resolution_status: str,
    ) -> dict[str, str]:
        return self._call("progress", record, checkin, resolution_status)

    def _call(self, method_name: str, *args):
        primary_method = getattr(self.primary, method_name)
        fallback_method = getattr(self.fallback, method_name)
        try:
            result = primary_method(*args)
            if result:
                return result
        except Exception:
            pass
        return fallback_method(*args)


class MeaningGeneratorProtocol:
    def diagnosis(self, intake: dict[str, Any], dna: dict[str, Any]) -> dict[str, str]:
        raise NotImplementedError

    def restructuring(
        self,
        diagnosis: dict[str, Any],
        old_cycle_map: dict[str, Any],
        dna: dict[str, Any] | None,
    ) -> dict[str, str]:
        raise NotImplementedError

    def action(self, restructuring: dict[str, Any]) -> dict[str, str]:
        raise NotImplementedError

    def progress(
        self,
        record: dict[str, Any],
        checkin: dict[str, Any],
        resolution_status: str,
    ) -> dict[str, str]:
        raise NotImplementedError


class HeuristicRussianMeaningGenerator(MeaningGeneratorProtocol):
    def diagnosis(self, intake: dict[str, Any], dna: dict[str, Any]) -> dict[str, str]:
        text = self._joined_text(intake)
        mechanism = self._detect_mechanism(text)
        diagnosis_by_mechanism = {
            "money_through_strain": {
                "old_belief_statement": "Больше денег приходит в основном через ещё большее напряжение.",
                "attention_bias_clue": "Внимание первым делом цепляется за тяжесть, объём работы и нехватку сил.",
                "behavior_pattern_clue": "Человек добавляет усилие раньше, чем делает более ясный запрос или меняет способ предъявления ценности.",
                "reinforcement_logic": "Слабый результат снова выглядит как доказательство, что деньги даются тяжело.",
                "hidden_prohibition_statement": "Получать легче ощущается небезопасно или как будто незаслуженно.",
            },
            "underpricing_visibility_avoidance": {
                "old_belief_statement": "Просить больше опасно, потому что это может привести к отказу или напряжению.",
                "attention_bias_clue": "Внимание ищет сигналы отказа, неудобства и риска показаться навязчивым.",
                "behavior_pattern_clue": "Человек смягчает цену, откладывает ясный оффер или уходит в лишние объяснения.",
                "reinforcement_logic": "Слабый доход снова подтверждает, что ясный запрос якобы опасен.",
                "hidden_prohibition_statement": "Видимость и прямое предъявление цены ощущаются как риск потери принятия.",
            },
            "free_value_leakage": {
                "old_belief_statement": "Сначала нужно дать много пользы бесплатно, и только потом можно говорить о деньгах.",
                "attention_bias_clue": "Внимание фиксируется на том, как быть полезным и удобным, а не на границе между бесплатным и платным.",
                "behavior_pattern_clue": "Человек долго консультирует бесплатно, прежде чем обозначить платный формат.",
                "reinforcement_logic": "Продажи срываются, и это снова выглядит как подтверждение, что про деньги говорить рано или неудобно.",
                "hidden_prohibition_statement": "Ранний разговор о деньгах ощущается как риск потерять контакт или симпатию.",
            },
            "deferred_money_conversation": {
                "old_belief_statement": "Про деньги лучше говорить позже, когда ценность уже будет доказана ещё сильнее.",
                "attention_bias_clue": "Внимание уходит в дополнительные доказательства ценности и подготовку вместо самого денежного разговора.",
                "behavior_pattern_clue": "Человек откладывает разговор о повышении, компенсации или пересмотре условий.",
                "reinforcement_logic": "Доход не меняется, и это снова выглядит как подтверждение, что для разговора о деньгах ещё рано.",
                "hidden_prohibition_statement": "Прямой разговор о деньгах ощущается как риск конфликта или потери статуса хорошего человека.",
            },
            "value_discount_when_easy": {
                "old_belief_statement": "Если мне легко, значит за это нельзя просить серьёзные деньги.",
                "attention_bias_clue": "Внимание обесценивает результат и цепляется за то, сколько усилий ушло, а не за ценность эффекта.",
                "behavior_pattern_clue": "Человек снижает цену или сомневается в ней, когда работа даётся быстро.",
                "reinforcement_logic": "Недооценённый доход снова подтверждает мысль, что лёгкая для меня работа не может стоить дорого.",
                "hidden_prohibition_statement": "Брать хорошие деньги за лёгкость ощущается как будто нечестно или слишком смело.",
            },
            "rejection_collapse_pricing": {
                "old_belief_statement": "Один отказ означает, что рынок не готов платить больше.",
                "attention_bias_clue": "Внимание резко фокусируется на отказах и быстро принимает их за объективный потолок рынка.",
                "behavior_pattern_clue": "После первых отказов человек автоматически снижает цену и отступает назад.",
                "reinforcement_logic": "Снижение цены снова закрепляет слабый доход и усиливает веру в невозможность держать более высокий уровень.",
                "hidden_prohibition_statement": "Выдерживать отказ без отката назад ощущается небезопасно.",
            },
            "sales_avoidance_preparation_loop": {
                "old_belief_statement": "Перед прямым оффером нужно ещё больше подготовиться, иначе продавать небезопасно.",
                "attention_bias_clue": "Внимание уходит в доработку, обучение и подготовку вместо прямого выхода к клиенту.",
                "behavior_pattern_clue": "Человек улучшает продукт и откладывает прямые предложения потенциальным клиентам.",
                "reinforcement_logic": "Продаж не происходит, и это снова подтверждает мысль, что пока ещё рано выходить с прямым оффером.",
                "hidden_prohibition_statement": "Прямая продажа ощущается как риск отказа, стыда или навязчивости.",
            },
            "safety_in_smallness": {
                "old_belief_statement": "Оставаться в маленьком масштабе безопаснее, чем реально расширяться.",
                "attention_bias_clue": "Внимание цепляется за причины не выходить из привычного потолка.",
                "behavior_pattern_clue": "Человек выбирает безопасные маленькие шаги и удерживает старый предел дохода.",
                "reinforcement_logic": "Низкий, но знакомый результат ощущается безопаснее, чем рост с неопределённостью.",
                "hidden_prohibition_statement": "Расширение воспринимается как риск потери контроля или устойчивости.",
            },
        }
        result = diagnosis_by_mechanism[mechanism].copy()
        return {
            "leading_mechanism_hypothesis": mechanism,
            **result,
            "diagnosis_confidence_note": f"Построено по intake и DNA-подсказкам: {', '.join(dna['hidden_structure_cues'])}.",
        }

    def restructuring(
        self,
        diagnosis: dict[str, Any],
        old_cycle_map: dict[str, Any],
        dna: dict[str, Any] | None,
    ) -> dict[str, str]:
        mechanism = diagnosis["leading_mechanism_hypothesis"]
        restructuring_by_mechanism = {
            "money_through_strain": {
                "new_belief": "Доход может расти не только через большее напряжение, но и через более ясное предъявление ценности.",
                "new_attention_target": "Замечать, где ценность уже есть, но пока не названа и не запрошена.",
                "new_behavior_direction": "Сделать один более чистый денежный запрос до того, как снова добавлять усилие.",
                "desired_result_marker": "Один конкретный момент, где ценность заявлена яснее.",
                "new_reinforcement_statement": "Новый результат может появиться без дополнительного перегруза.",
            },
            "underpricing_visibility_avoidance": {
                "new_belief": "Ясный запрос или цена могут быть безопасными, даже если не каждый запрос приводит к согласию.",
                "new_attention_target": "Замечать, где доход тормозится не рынком, а неясностью предложения или цены.",
                "new_behavior_direction": "Один раз назвать цену прямее и чище, без смягчения.",
                "desired_result_marker": "Один эпизод более ясной цены или денежного запроса.",
                "new_reinforcement_statement": "Даже частичный отклик уже доказывает, что ясность полезнее смягчения.",
            },
            "free_value_leakage": {
                "new_belief": "Я могу обозначать границу между полезным контактом и платным форматом раньше, не разрушая доверие.",
                "new_attention_target": "Замечать момент, когда бесплатная польза уже достаточна, а разговор пора переводить в платный формат.",
                "new_behavior_direction": "Один раз раньше обозначить платный следующий шаг вместо длинной бесплатной консультации.",
                "desired_result_marker": "Один разговор, где платный формат назван вовремя.",
                "new_reinforcement_statement": "Раннее обозначение денег может усиливать ясность, а не разрушать контакт.",
            },
            "deferred_money_conversation": {
                "new_belief": "Разговор о деньгах может быть частью нормальной рабочей ясности, а не наградой только после ещё одного доказательства.",
                "new_attention_target": "Замечать, где я откладываю денежный разговор под видом дополнительной подготовки.",
                "new_behavior_direction": "Один раз назначить или открыть прямой разговор о пересмотре денег без лишнего откладывания.",
                "desired_result_marker": "Один назначенный или начатый разговор о деньгах.",
                "new_reinforcement_statement": "Ясный разговор о деньгах может двигать доход быстрее, чем бесконечное дополнительное доказательство.",
            },
            "value_discount_when_easy": {
                "new_belief": "Лёгкость для меня не отменяет ценность результата для клиента.",
                "new_attention_target": "Замечать ценность результата, а не путать цену с количеством личного напряжения.",
                "new_behavior_direction": "Один раз опереться на ценность результата, а не на тяжесть процесса, когда называю деньги.",
                "desired_result_marker": "Одна формулировка цены через результат, а не через часы и тяжесть.",
                "new_reinforcement_statement": "Если результат ценен, он может стоить денег даже тогда, когда мне самому работа далась легко.",
            },
            "rejection_collapse_pricing": {
                "new_belief": "Один отказ не обязан автоматически определять мой денежный потолок.",
                "new_attention_target": "Замечать, где отказ превращается в общий вывод о невозможности держать цену.",
                "new_behavior_direction": "Один раз удержать прежний денежный уровень после отказа, не снижая его автоматически.",
                "desired_result_marker": "Один повторный шаг без автоматического отката по цене.",
                "new_reinforcement_statement": "Отказ можно выдерживать без мгновенного снижения планки.",
            },
            "sales_avoidance_preparation_loop": {
                "new_belief": "Один прямой оффер может быть полезнее, чем ещё один круг подготовки.",
                "new_attention_target": "Замечать, где подготовка уже перестала усиливать качество и стала способом отложить продажу.",
                "new_behavior_direction": "Сделать один прямой оффер без дополнительного круга подготовки.",
                "desired_result_marker": "Один отправленный прямой оффер потенциальному клиенту.",
                "new_reinforcement_statement": "Прямой выход в продажу даёт реальный сигнал лучше, чем бесконечная доработка в одиночку.",
            },
            "safety_in_smallness": {
                "new_belief": "Маленькое расширение можно выдержать безопасно.",
                "new_attention_target": "Замечать одно место, где ограничение работает автоматически, а не реально необходимо.",
                "new_behavior_direction": "Сделать один контролируемый шаг за предел текущего маленького потолка.",
                "desired_result_marker": "Один ограниченный шаг, который слегка расширяет прежнюю норму.",
                "new_reinforcement_statement": "Расширение может быть дозированным и переносимым.",
            },
        }
        result = restructuring_by_mechanism[mechanism].copy()
        if dna and dna["phrasing_constraints"]:
            result["new_reinforcement_statement"] = (
                f"{result['new_reinforcement_statement']} Условие формулировки: {dna['phrasing_constraints'][0]}."
            )
        return result

    def action(self, restructuring: dict[str, Any]) -> dict[str, str]:
        behavior = restructuring["new_behavior_direction"].lower()
        belief = restructuring["new_belief"].lower()
        if "расшир" in behavior or "потол" in behavior or "контролируемый шаг" in behavior:
            action = "Сделай один ограниченный шаг на расширение, который раньше откладывался из осторожности."
            criterion = "Один конкретный шаг на расширение за предел старого потолка выполнен и зафиксирован."
        elif "платн" in behavior or "бесплат" in behavior:
            action = "В следующем разговоре после первой полезной подсказки одной фразой обозначь платный следующий шаг."
            criterion = "В одном реальном разговоре или переписке платный формат назван до того, как ты снова ушёл в длинную бесплатную помощь."
        elif "пересмотр" in behavior or "разговор о деньгах" in behavior:
            action = "Сегодня назначь или начни один прямой разговор о пересмотре денег без дополнительного откладывания."
            criterion = "Один конкретный разговор о повышении, компенсации или пересмотре условий инициирован сообщением или устно."
        elif "результат" in belief and "лёгк" in belief:
            action = "В одном денежном разговоре назови цену через ценность результата и не оправдывай её количеством часов."
            criterion = "Одна цена или сумма названа с опорой на результат для клиента, без оправдания через собственное напряжение."
        elif "отказ" in belief:
            action = "Сделай один повторный денежный шаг без автоматического снижения цены после отказа."
            criterion = "После одного отказа ты сохранил прежний уровень цены хотя бы в одном следующем сообщении, предложении или разговоре."
        elif "оффер" in behavior or "продаж" in behavior:
            action = "Отправь один прямой оффер потенциальному клиенту без дополнительного круга подготовки."
            criterion = "Один конкретный оффер отправлен потенциальному клиенту в явной форме."
        elif "цен" in behavior or "запрос" in behavior:
            action = "Один раз прямо назови цену или денежный запрос без смягчения и лишних оправданий."
            criterion = "Одна конкретная цена, сумма или денежный запрос реально озвучены или отправлены."
        else:
            action = "Назови один конкретный элемент своей ценности в письменной форме или в разговоре."
            criterion = "Одна чёткая формулировка ценности реально произнесена или отправлена."
        return {
            "action": action,
            "completion_criterion": criterion,
            "timeframe": "в течение 24 часов",
            "failure_risk_note": "Главный риск - снова уйти в лишние усилия или объяснения вместо одного чистого шага.",
        }

    def progress(
        self,
        record: dict[str, Any],
        checkin: dict[str, Any],
        resolution_status: str,
    ) -> dict[str, str]:
        if resolution_status == "completed_shifted":
            shift = "Есть заметный сдвиг: пользователь выдержал новый шаг и получил подтверждение новой модели."
            barrier = "Следующий цикл стоит держать таким же узким, чтобы закрепить переносимость нового действия."
        elif resolution_status == "completed_partial":
            shift = "Движение произошло, но новая модель пока не стала устойчивой."
            barrier = "Старый цикл всё ещё частично перехватывает внимание и поведение."
        else:
            shift = "Заметного сдвига пока не произошло."
            barrier = "Старый цикл остался доминирующим во время попытки действия."
        return {
            "shift_marker": shift,
            "remaining_barrier": barrier,
            "memory_update_note": "Результат цикла сохранён для следующего прохода.",
        }

    def _joined_text(self, intake: dict[str, Any]) -> str:
        return " ".join(
            [
                intake.get("problem_summary", ""),
                intake.get("repeated_pattern_summary", ""),
                intake.get("source_excerpt") or "",
            ]
        ).lower()

    def _detect_mechanism(self, text: str) -> str:
        scores = {
            "money_through_strain": self._score(
                text,
                "много работ",
                "впах",
                "перегруз",
                "устал",
                "выгора",
                "ещё сильнее",
                "еще сильнее",
                "тяжел",
                "тяжёл",
                "паш",
                "доказы",
                "тащу",
                "перерабат",
            ),
            "underpricing_visibility_avoidance": self._score(
                text,
                "цена",
                "цену",
                "стоим",
                "сумм",
                "просить",
                "прошу",
                "запрос",
                "оффер",
                "продаж",
                "прода",
                "назвать сумму",
                "смягча",
            ),
            "free_value_leakage": self._score(
                text,
                "бесплат",
                "бесплатно",
                "много помогаю",
                "консультир",
                "совет",
                "сначала отдаю",
                "потом теряю",
                "платный формат",
            ),
            "deferred_money_conversation": self._score(
                text,
                "отклады",
                "позже",
                "доказать ценность",
                "компенсац",
                "пересмотр",
                "повышен",
                "повышение",
                "разговор о деньгах",
                "не поднимал вопрос",
                "надо еще",
                "надо ещё",
            ),
            "value_discount_when_easy": self._score(
                text,
                "слишком легк",
                "слишком лёгк",
                "делаю быстро",
                "легко для меня",
                "нельзя просить",
                "не может стоить",
                "быстро",
                "легкая задача",
                "лёгкая задача",
            ),
            "rejection_collapse_pricing": self._score(
                text,
                "отказ",
                "отказов",
                "после первого",
                "после нескольких отказов",
                "рынок не готов",
                "снижаю цену",
                "не лезть выше",
                "холодного ответа",
            ),
            "sales_avoidance_preparation_loop": self._score(
                text,
                "боюсь продаж",
                "прямых предложениях",
                "долго готовлюсь",
                "улучшаю продукт",
                "избегаю писать",
                "потенциальным клиентам",
                "дополнительного круга подготовки",
                "подготовк",
            ),
            "safety_in_smallness": self._score(
                text,
                "безопас",
                "маленьк",
                "масштаб",
                "расшир",
                "тормож",
                "потолок",
                "стабильн",
                "маленькие действия",
            ),
        }
        best_mechanism = max(scores, key=scores.get)
        if scores[best_mechanism] <= 0:
            return "safety_in_smallness"
        return best_mechanism

    def _score(self, text: str, *tokens: str) -> int:
        return sum(1 for token in tokens if token in text)


@dataclass
class OpenAIResponsesMeaningGenerator(MeaningGeneratorProtocol):
    api_key: str | None
    model: str
    base_url: str
    timeout_seconds: int = 30

    @classmethod
    def from_env(cls) -> "OpenAIResponsesMeaningGenerator":
        return cls(
            api_key=os.environ.get("OPENAI_API_KEY"),
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            timeout_seconds=int(os.environ.get("OPENAI_TIMEOUT_SECONDS", "30")),
        )

    def diagnosis(self, intake: dict[str, Any], dna: dict[str, Any]) -> dict[str, str]:
        payload = {
            "intake": intake,
            "dna": dna,
        }
        schema = _schema(
            "diagnosis_output_ru",
            {
                "leading_mechanism_hypothesis": {"type": "string"},
                "old_belief_statement": {"type": "string"},
                "attention_bias_clue": {"type": "string"},
                "behavior_pattern_clue": {"type": "string"},
                "reinforcement_logic": {"type": "string"},
                "hidden_prohibition_statement": {"type": "string"},
                "diagnosis_confidence_note": {"type": "string"},
            },
        )
        system = (
            "Ты создаёшь только один артефакт Diagnosis Output для продукта о перестройке денежного цикла. "
            "Пиши только по-русски. Дай ровно одну ведущую гипотезу механизма, без списков альтернатив, "
            "без советов, без действий, без изменения сценария beyond money/income. "
            "Старайся различать реальные денежные паттерны: перегруз ради денег, избегание цены, "
            "слив ценности бесплатно, откладывание денежного разговора, обесценивание лёгкого результата, "
            "откат после отказа, избегание прямого оффера."
        )
        return self._request_json(schema_name="diagnosis_output_ru", system_prompt=system, user_payload=payload, schema=schema)

    def restructuring(
        self,
        diagnosis: dict[str, Any],
        old_cycle_map: dict[str, Any],
        dna: dict[str, Any] | None,
    ) -> dict[str, str]:
        payload = {
            "diagnosis": diagnosis,
            "old_cycle_map": old_cycle_map,
            "dna": dna,
        }
        schema = _schema(
            "restructuring_output_ru",
            {
                "new_belief": {"type": "string"},
                "new_attention_target": {"type": "string"},
                "new_behavior_direction": {"type": "string"},
                "desired_result_marker": {"type": "string"},
                "new_reinforcement_statement": {"type": "string"},
            },
        )
        system = (
            "Ты создаёшь только один артефакт Restructuring Output для русского продукта про деньги и доход. "
            "Пиши только по-русски. Новая формулировка должна быть психологически допустимой, "
            "не экстремальной, без действий, без нескольких вариантов. "
            "Избегай слишком общей терапии и общих фраз про самоценность; перестройка должна быть привязана к денежному паттерну кейса."
        )
        return self._request_json(schema_name="restructuring_output_ru", system_prompt=system, user_payload=payload, schema=schema)

    def action(self, restructuring: dict[str, Any]) -> dict[str, str]:
        payload = {"restructuring": restructuring}
        schema = _schema(
            "action_output_ru",
            {
                "action": {"type": "string"},
                "completion_criterion": {"type": "string"},
                "timeframe": {"type": "string"},
                "failure_risk_note": {"type": "string"},
            },
        )
        system = (
            "Ты создаёшь только один артефакт Action Output для русского продукта про деньги и доход. "
            "Пиши только по-русски. Разрешено только одно конкретное действие. "
            "Не создавай список шагов, не добавляй второй action, не переосмысляй диагноз. "
            "Действие должно быть рычажным, проверяемым в одном шаге, без расплывчатых формулировок вроде "
            "'осознай', 'подумай', 'проанализируй', 'начни относиться иначе'."
        )
        return self._request_json(schema_name="action_output_ru", system_prompt=system, user_payload=payload, schema=schema)

    def progress(
        self,
        record: dict[str, Any],
        checkin: dict[str, Any],
        resolution_status: str,
    ) -> dict[str, str]:
        payload = {
            "resolution_status": resolution_status,
            "diagnosis_output": record["diagnosis_output"],
            "restructuring_output": record["restructuring_output"],
            "action_output": record["action_output"],
            "checkin_output": checkin,
        }
        schema = _schema(
            "progress_snapshot_ru",
            {
                "shift_marker": {"type": "string"},
                "remaining_barrier": {"type": "string"},
                "memory_update_note": {"type": "string"},
            },
        )
        system = (
            "Ты создаёшь только текстовые поля для Progress Snapshot в русском продукте про деньги и доход. "
            "Статус уже определён детерминированным кодом и его нельзя менять. "
            "Пиши только по-русски, кратко и операционно. "
            "Не уходи в общую мотивацию; фиксируй конкретный сдвиг или конкретный оставшийся барьер."
        )
        return self._request_json(schema_name="progress_snapshot_ru", system_prompt=system, user_payload=payload, schema=schema)

    def _request_json(
        self,
        *,
        schema_name: str,
        system_prompt: str,
        user_payload: dict[str, Any],
        schema: dict[str, Any],
    ) -> dict[str, str]:
        if not self.api_key:
            raise MeaningGenerationError("OPENAI_API_KEY is not configured.")
        endpoint = self.base_url.rstrip("/") + "/responses"
        body = {
            "model": self.model,
            "store": False,
            "input": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        "Сгенерируй только структуру, соответствующую схеме. "
                        "Все значения должны быть на русском языке.\n\n"
                        + json.dumps(user_payload, ensure_ascii=False)
                    ),
                },
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                }
            },
        }
        req = request.Request(
            endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            raise MeaningGenerationError(str(exc)) from exc
        text = self._extract_output_text(payload)
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise MeaningGenerationError("Model output was not valid JSON.") from exc
        if not isinstance(parsed, dict):
            raise MeaningGenerationError("Model output was not a JSON object.")
        return parsed

    def _extract_output_text(self, payload: dict[str, Any]) -> str:
        for output in payload.get("output", []):
            if output.get("type") != "message":
                continue
            for content in output.get("content", []):
                if content.get("type") == "output_text":
                    text = content.get("text")
                    if isinstance(text, str) and text.strip():
                        return text
        raise MeaningGenerationError("No structured output text returned.")


def _schema(name: str, properties: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties.keys()),
        "additionalProperties": False,
    }
