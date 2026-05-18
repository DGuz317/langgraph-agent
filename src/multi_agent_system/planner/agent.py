from typing import Any
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage

from multi_agent_system.common.llm import get_llm
from multi_agent_system.planner.prompts import PLANNER_SYSTEM_PROMPT
from multi_agent_system.planner.schemas import PlannedTask, PlannerOutput


class PlannerAgent:
    def __init__(self) -> None:
        self.llm = get_llm()
        self.structured_llm = None

    async def ainvoke(self, user_input: str) -> PlannerOutput:
        try:
            output = await self._invoke_planner_once(user_input)
            return self._normalize_output(output)

        except Exception as first_error:
            try:
                repaired_output = await self._repair_planner_output(
                    user_input=user_input,
                    error=first_error,
                )
                return self._normalize_output(repaired_output)

            except Exception as repair_error:
                return self._safe_failed_output(
                    user_input=user_input,
                    error=repair_error,
                )

    async def _invoke_planner_once(self, user_input: str) -> PlannerOutput:
        structured_llm = self._get_structured_llm()

        result = await structured_llm.ainvoke(
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

        return self._coerce_planner_output(result)

    async def _repair_planner_output(
        self,
        *,
        user_input: str,
        error: Exception,
    ) -> PlannerOutput:
        structured_llm = self._get_structured_llm()
        repair_prompt = self._build_repair_prompt(
            user_input=user_input,
            error=error,
        )

        result = await structured_llm.ainvoke(
            [
                SystemMessage(content=PLANNER_SYSTEM_PROMPT),
                HumanMessage(content=repair_prompt),
            ]
        )

        return self._coerce_planner_output(result)

    def _get_structured_llm(self):
        if self.structured_llm is not None:
            return self.structured_llm

        with_structured_output = getattr(
            self.llm,
            "with_structured_output",
            None,
        )

        if not callable(with_structured_output):
            raise TypeError(
                "Configured LLM does not support with_structured_output()."
            )

        self.structured_llm = with_structured_output(PlannerOutput)
        return self.structured_llm

    def _coerce_planner_output(self, value: Any) -> PlannerOutput:
        if isinstance(value, PlannerOutput):
            return value

        if isinstance(value, dict):
            return PlannerOutput.model_validate(value)

        model_dump = getattr(value, "model_dump", None)
        if callable(model_dump):
            return PlannerOutput.model_validate(model_dump())

        raise TypeError(
            "Planner LLM returned unsupported output type: "
            f"{type(value).__name__}."
        )

    def _build_repair_prompt(
        self,
        *,
        user_input: str,
        error: Exception,
    ) -> str:
        return (
            "The previous planner output was invalid. "
            "Return a corrected PlannerOutput that satisfies the schema.\n\n"
            f"Original user input:\n{user_input}\n\n"
            f"Validation error:\n{error}\n\n"
            "Repair rules:\n"
            "- Use only agent values: invoice, music.\n"
            "- Use only valid intents for each agent.\n"
            "- Every executable task must include required args.\n"
            "- If required args are missing, include them in task.missing_fields.\n"
            "- For generic music recommendations, use intent=clarify_music_search "
            "and missing_fields=[\"music_search_type\"].\n"
            "- For unrelated/help queries, return tasks=[].\n"
            "- Return only the structured PlannerOutput."
        )

    def _safe_failed_output(
        self,
        *,
        user_input: str,
        error: Exception,
    ) -> PlannerOutput:
        return PlannerOutput(
            status="failed",
            tasks=[],
            confidence=0.0,
            requires_aggregation=False,
            missing_fields=[],
        )

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
            status=output.status,
            tasks=tasks,
            confidence=output.confidence,
            requires_aggregation=len(tasks) > 1,
            missing_fields=missing_fields,
        )
        