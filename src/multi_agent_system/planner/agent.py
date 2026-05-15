from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage

from multi_agent_system.common.llm import get_llm
from multi_agent_system.planner.prompts import PLANNER_SYSTEM_PROMPT
from multi_agent_system.planner.schemas import PlannedTask, PlannerOutput


class PlannerAgent:
    VALID_INVOICE_INTENTS = {
        "latest_invoice",
        "invoices_by_unit_price",
    }

    VALID_MUSIC_INTENTS = {
        "tracks_by_artist",
        "albums_by_artist",
        "songs_by_genre",
        "check_song",
        "clarify_music_search",
    }

    VALID_INTENTS = VALID_INVOICE_INTENTS | VALID_MUSIC_INTENTS

    def __init__(self) -> None:
        self.llm = get_llm()

    def invoke(self, user_input: str) -> PlannerOutput:
        return self._invoke_llm(user_input)

    def _invoke_llm(self, user_input: str) -> PlannerOutput:
        if self.llm is None:
            raise RuntimeError("LLM is not initialized.")

        structured_llm = self.llm.with_structured_output(PlannerOutput)

        output = self._invoke_structured_planner(
            structured_llm=structured_llm,
            user_input=user_input,
        )

        try:
            normalized_output = self._normalize_output(output)
            self._validate_llm_output(normalized_output)
            return normalized_output
        except ValueError:
            repaired_output = self._invoke_structured_planner(
                structured_llm=structured_llm,
                user_input=(
                    "The previous planner output was invalid or empty.\n"
                    "Re-plan the user request and follow the system prompt exactly.\n"
                    "If the request is a generic music recommendation, return a "
                    "clarify_music_search task with missing_fields=[\"music_search_type\"].\n\n"
                    f"User request: {user_input}"
                ),
            )

            normalized_output = self._normalize_output(repaired_output)
            self._validate_llm_output(normalized_output)
            return normalized_output

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

    def _validate_llm_output(self, output: PlannerOutput) -> None:
        for task in output.tasks:
            self._validate_intent(task)
            self._validate_agent_intent_pair(task)
            self._validate_instruction(task)

    def _validate_intent(self, task: PlannedTask) -> None:
        if task.intent not in self.VALID_INTENTS:
            raise ValueError(
                "LLM planner returned invalid intent.\n"
                f"Task: {task.model_dump_json(indent=2)}"
            )

    def _validate_agent_intent_pair(self, task: PlannedTask) -> None:
        if task.agent == "invoice" and task.intent not in self.VALID_INVOICE_INTENTS:
            raise ValueError(
                "LLM planner assigned non-invoice intent to invoice agent.\n"
                f"Task: {task.model_dump_json(indent=2)}"
            )

        if task.agent == "music" and task.intent not in self.VALID_MUSIC_INTENTS:
            raise ValueError(
                "LLM planner assigned non-music intent to music agent.\n"
                f"Task: {task.model_dump_json(indent=2)}"
            )

    def _validate_instruction(self, task: PlannedTask) -> None:
        if not task.instruction.strip():
            raise ValueError(
                "LLM planner created task with empty instruction.\n"
                f"Task: {task.model_dump_json(indent=2)}"
            )

        if task.agent == "invoice" and "invoice" not in task.instruction.lower():
            raise ValueError(
                "LLM planner created invoice task with unclear instruction.\n"
                f"Task: {task.model_dump_json(indent=2)}"
            )
    
    def _invoke_structured_planner(
        self,
        structured_llm,
        user_input: str,
    ) -> PlannerOutput:
        output = structured_llm.invoke(
            [
                SystemMessage(content=PLANNER_SYSTEM_PROMPT),
                HumanMessage(
                    content=(
                        "Return a valid PlannerOutput for the following request.\n"
                        "Do not include explanations outside the structured output.\n\n"
                        f"{user_input}"
                    )
                ),
            ]
        )

        if isinstance(output, PlannerOutput):
            return output

        return PlannerOutput.model_validate(output)