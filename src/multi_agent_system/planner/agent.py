import re
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage

from multi_agent_system.common.llm import get_llm
from multi_agent_system.planner.prompts import PLANNER_SYSTEM_PROMPT
from multi_agent_system.planner.schemas import PlannedTask, PlannerOutput


class PlannerAgent:
    def __init__(
        self,
        use_llm: bool = True,
        fallback_to_deterministic: bool = False,
    ) -> None:
        self.use_llm = use_llm
        self.fallback_to_deterministic = fallback_to_deterministic
        self.llm = get_llm() if use_llm else None

    def _normalize_output(self, output: PlannerOutput) -> PlannerOutput:
        tasks: list[PlannedTask] = []

        for task in output.tasks:
            task.id = task.id or str(uuid4())
            task.status = "not_started"
            tasks.append(task)

        missing_fields = sorted(
            {
                field
                for task in tasks
                for field in task.missing_fields
            }
        )

        return PlannerOutput(
            status="completed",
            tasks=tasks,
            confidence=output.confidence,
            requires_aggregation=len(tasks) > 1,
            missing_fields=missing_fields,
        )

    def _validate_llm_output(self, user_input: str, output: PlannerOutput) -> None:
        text = user_input.lower()

        domain_keywords = [
            "invoice",
            "billing",
            "customer_id",
            "customer id",
            "song",
            "songs",
            "track",
            "tracks",
            "album",
            "albums",
            "artist",
            "genre",
            "music",
            "rock",
            "jazz",
            "metal",
        ]

        looks_supported = any(keyword in text for keyword in domain_keywords)

        if looks_supported and not output.tasks:
            raise ValueError(
                "LLM planner returned no tasks for a supported request.\n"
                f"User input: {user_input}\n"
                f"Planner output: {output.model_dump_json(indent=2)}"
            )

        valid_intents = {
            "latest_invoice",
            "invoices_by_unit_price",
            "support_employee",
            "tracks_by_artist",
            "albums_by_artist",
            "songs_by_genre",
            "check_song",
        }

        for task in output.tasks:
            if task.intent not in valid_intents:
                raise ValueError(
                    "LLM planner returned invalid intent.\n"
                    f"Task: {task.model_dump_json(indent=2)}"
                )

            if task.agent == "invoice" and task.intent not in {
                "latest_invoice",
                "invoices_by_unit_price",
                "support_employee",
            }:
                raise ValueError(
                    "LLM planner assigned non-invoice intent to invoice agent.\n"
                    f"Task: {task.model_dump_json(indent=2)}"
                )

            if task.agent == "music" and task.intent not in {
                "tracks_by_artist",
                "albums_by_artist",
                "songs_by_genre",
                "check_song",
            }:
                raise ValueError(
                    "LLM planner assigned non-music intent to music agent.\n"
                    f"Task: {task.model_dump_json(indent=2)}"
                )

            if task.agent == "invoice" and "invoice" not in task.instruction.lower():
                raise ValueError(
                    "LLM planner created invoice task with unclear instruction.\n"
                    f"Task: {task.model_dump_json(indent=2)}"
                )

            if task.agent == "music" and not task.instruction.strip():
                raise ValueError(
                    "LLM planner created music task with empty instruction.\n"
                    f"Task: {task.model_dump_json(indent=2)}"
                )

    def invoke(self, user_input: str) -> PlannerOutput:
        if not self.use_llm:
            return self._invoke_deterministic(user_input)

        if self.fallback_to_deterministic:
            try:
                return self._invoke_llm(user_input)
            except Exception:
                return self._invoke_deterministic(user_input)

        return self._invoke_llm(user_input)

    def _invoke_llm(self, user_input: str) -> PlannerOutput:
        if self.llm is None:
            raise RuntimeError("LLM is not initialized.")

        structured_llm = self.llm.with_structured_output(PlannerOutput)

        output = structured_llm.invoke(
            [
                SystemMessage(content=PLANNER_SYSTEM_PROMPT),
                HumanMessage(content=user_input),
            ]
        )

        if not isinstance(output, PlannerOutput):
            output = PlannerOutput.model_validate(output)

        output = self._normalize_output(output)
        self._validate_llm_output(user_input, output)

        return output

    def debug_raw_llm(self, user_input: str) -> str:
        if self.llm is None:
            raise RuntimeError("LLM is not initialized.")

        response = self.llm.invoke(
            [
                SystemMessage(content=PLANNER_SYSTEM_PROMPT),
                HumanMessage(
                    content=(
                        "Return the planner output as JSON only.\n\n"
                        f"User request: {user_input}"
                    )
                ),
            ]
        )

        return str(response.content)

    def _invoke_deterministic(self, user_input: str) -> PlannerOutput:
        text = user_input.lower()
        tasks: list[PlannedTask] = []

        if self._is_invoice_request(text):
            tasks.append(
                PlannedTask(
                    id=str(uuid4()),
                    agent="invoice",
                    intent=self._detect_invoice_intent(text),
                    instruction=self._build_invoice_instruction(user_input),
                    missing_fields=self._missing_invoice_fields(user_input),
                )
            )

        if self._is_music_request(text):
            music_intent = self._detect_music_intent(text)

            tasks.append(
                PlannedTask(
                    id=str(uuid4()),
                    agent="music",
                    intent=music_intent,
                    instruction=self._build_music_instruction(user_input, music_intent),
                    missing_fields=self._missing_music_fields(user_input, music_intent),
                )
            )

        if not tasks:
            return PlannerOutput(
                tasks=[],
                confidence=0.0,
                requires_aggregation=False,
                missing_fields=[],
            )

        missing_fields = sorted(
            {
                field
                for task in tasks
                for field in task.missing_fields
            }
        )

        return PlannerOutput(
            tasks=tasks,
            confidence=0.75,
            requires_aggregation=len(tasks) > 1,
            missing_fields=missing_fields,
        )

    def _is_invoice_request(self, text: str) -> bool:
        keywords = ["invoice", "billing", "unit price", "customer id", "customer_id"]
        return any(keyword in text for keyword in keywords)

    def _is_music_request(self, text: str) -> bool:
        keywords = [
            "music",
            "song",
            "songs",
            "track",
            "tracks",
            "album",
            "albums",
            "artist",
            "genre",
            "rock",
            "jazz",
            "metal",
            "ac/dc",
            "queen",
        ]
        return any(keyword in text for keyword in keywords)

    def _detect_invoice_intent(self, text: str):
        if "employee" in text or "support rep" in text:
            return "support_employee"

        if "unit price" in text or "highest price" in text:
            return "invoices_by_unit_price"

        return "latest_invoice"

    def _detect_music_intent(self, text: str):
        if "album" in text or "albums" in text:
            return "albums_by_artist"

        if "genre" in text or "rock" in text or "jazz" in text or "metal" in text:
            return "songs_by_genre"

        if "check" in text or "exists" in text or "do you have" in text:
            return "check_song"

        return "tracks_by_artist"

    def _missing_invoice_fields(self, user_input: str) -> list[str]:
        text = user_input.lower()
        intent = self._detect_invoice_intent(text)

        missing: list[str] = []

        if not self._extract_number(user_input, ["customer_id", "customer id", "id"]):
            missing.append("customer_id")

        if intent == "support_employee":
            if not self._extract_number(user_input, ["invoice_id", "invoice id"]):
                missing.append("invoice_id")

        return missing

    def _missing_music_fields(self, user_input: str, intent: str) -> list[str]:
        text = user_input.lower()

        if intent == "songs_by_genre":
            if "rock" in text or "jazz" in text or "metal" in text or "genre" in text:
                return []
            return ["genre"]

        if intent == "check_song":
            return []

        if "artist" in text or "by " in text or "ac/dc" in text or "queen" in text:
            return []

        return ["artist"]

    def _build_invoice_instruction(self, user_input: str) -> str:
        text = user_input.lower()
        intent = self._detect_invoice_intent(text)

        customer_id = self._extract_number(
            user_input,
            ["customer_id", "customer id", "id"],
        )

        invoice_id = self._extract_number(
            user_input,
            ["invoice_id", "invoice id"],
        )

        if intent == "support_employee":
            return (
                f"Find employee for invoice_id={invoice_id} "
                f"and customer_id={customer_id}"
            )

        if intent == "invoices_by_unit_price":
            return f"Show invoices for customer_id={customer_id} sorted by unit price"

        return f"Get latest invoice for customer_id={customer_id}"

    def _build_music_instruction(self, user_input: str, intent: str) -> str:
        return user_input

    def _extract_number(self, text: str, field_names: list[str]) -> str | None:
        normalized = text.lower()

        for field_name in field_names:
            pattern = rf"{re.escape(field_name)}\s*(?:=|:|is)?\s*(\d+)"
            match = re.search(pattern, normalized)

            if match:
                return match.group(1)

        return None