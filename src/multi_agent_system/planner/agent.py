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
        if not use_llm:
            raise ValueError("PlannerAgent is LLM-only; use_llm=False is not supported.")

        if fallback_to_deterministic:
            raise ValueError("Deterministic planner fallback has been removed.")

        self.llm = get_llm()

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
        self._validate_llm_output(output)

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
