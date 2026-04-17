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
        text = f"{intake['problem_summary']} {intake['repeated_pattern_summary']}".lower()
        if any(token in text for token in ("тяж", "впах", "много работ", "паш", "выжива")):
            mechanism = "money_through_strain"
            old_belief = "Больше денег приходит в основном через ещё большее напряжение."
            attention = "Внимание первым делом цепляется за тяжесть, объём работы и нехватку сил."
            behavior = "Человек добавляет усилие раньше, чем делает более ясный запрос или меняет способ предъявления ценности."
            reinforcement = "Слабый результат снова выглядит как доказательство, что деньги даются тяжело."
            hidden = "Получать легче ощущается небезопасно или как будто незаслуженно."
        elif any(token in text for token in ("цен", "стоим", "прос", "откаж", "предлож", "прода")):
            mechanism = "underpricing_visibility_avoidance"
            old_belief = "Просить больше опасно, потому что это может привести к отказу или напряжению."
            attention = "Внимание ищет сигналы отказа, неудобства и риска показаться навязчивым."
            behavior = "Человек смягчает цену, откладывает ясный оффер или уходит в лишние объяснения."
            reinforcement = "Слабый доход снова подтверждает, что ясный запрос якобы опасен."
            hidden = "Видимость и прямое предъявление цены ощущаются как риск потери принятия."
        else:
            mechanism = "safety_in_smallness"
            old_belief = "Оставаться в маленьком масштабе безопаснее, чем реально расширяться."
            attention = "Внимание цепляется за причины не выходить из привычного потолка."
            behavior = "Человек выбирает безопасные маленькие шаги и удерживает старый предел дохода."
            reinforcement = "Низкий, но знакомый результат ощущается безопаснее, чем рост с неопределённостью."
            hidden = "Расширение воспринимается как риск потери контроля или устойчивости."
        return {
            "leading_mechanism_hypothesis": mechanism,
            "old_belief_statement": old_belief,
            "attention_bias_clue": attention,
            "behavior_pattern_clue": behavior,
            "reinforcement_logic": reinforcement,
            "hidden_prohibition_statement": hidden,
            "diagnosis_confidence_note": f"Построено по intake и DNA-подсказкам: {', '.join(dna['hidden_structure_cues'])}.",
        }

    def restructuring(
        self,
        diagnosis: dict[str, Any],
        old_cycle_map: dict[str, Any],
        dna: dict[str, Any] | None,
    ) -> dict[str, str]:
        mechanism = diagnosis["leading_mechanism_hypothesis"]
        if mechanism == "money_through_strain":
            new_belief = "Доход может расти не только через большее напряжение, но и через более ясное предъявление ценности."
            attention = "Замечать, где ценность уже есть, но пока не названа и не запрошена."
            behavior = "Сделать один более чистый денежный запрос до того, как снова добавлять усилие."
            result = "Один конкретный момент, где ценность заявлена яснее."
            reinforcement = "Новый результат может появиться без дополнительного перегруза."
        elif mechanism == "underpricing_visibility_avoidance":
            new_belief = "Ясный запрос или цена могут быть безопасными, даже если не каждый запрос приводит к согласию."
            attention = "Замечать, где доход тормозится не рынком, а неясностью предложения или цены."
            behavior = "Один раз назвать цену или оффер прямее и чище."
            result = "Один эпизод более ясного запроса или цены."
            reinforcement = "Даже частичный отклик уже доказывает, что ясность полезнее смягчения."
        else:
            new_belief = "Маленькое расширение можно выдержать безопасно."
            attention = "Замечать одно место, где ограничение работает автоматически, а не реально необходимо."
            behavior = "Сделать один контролируемый шаг за предел текущего маленького потолка."
            result = "Один ограниченный шаг, который слегка расширяет прежнюю норму."
            reinforcement = "Расширение может быть дозированным и переносимым."
        if dna and dna["phrasing_constraints"]:
            reinforcement = f"{reinforcement} Условие формулировки: {dna['phrasing_constraints'][0]}."
        return {
            "new_belief": new_belief,
            "new_attention_target": attention,
            "new_behavior_direction": behavior,
            "desired_result_marker": result,
            "new_reinforcement_statement": reinforcement,
        }

    def action(self, restructuring: dict[str, Any]) -> dict[str, str]:
        behavior = restructuring["new_behavior_direction"].lower()
        if "цен" in behavior or "запрос" in behavior or "оффер" in behavior:
            action = "Сделай один ясный денежный запрос или назови цену без лишних оправданий."
            criterion = "Один конкретный запрос, сообщение, предложение или озвученная цена реально отправлены."
        elif "расшир" in behavior:
            action = "Сделай один ограниченный шаг на расширение, который раньше откладывался из осторожности."
            criterion = "Один конкретный шаг за предел старого потолка выполнен и зафиксирован."
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
            "без советов, без действий, без изменения сценария beyond money/income."
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
            "не экстремальной, без действий, без нескольких вариантов."
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
            "Не создавай список шагов, не добавляй второй action, не переосмысляй диагноз."
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
            "Пиши только по-русски, кратко и операционно."
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
