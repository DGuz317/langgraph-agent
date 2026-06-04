from typing import Any
from uuid import uuid4

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from multi_agent_system.common.llm import get_llm
from multi_agent_system.common.observability import trace_config
from multi_agent_system.common.runnable import ainvoke_with_optional_config
from multi_agent_system.planner.prompts import (
    PLANNER_REPAIR_PROMPT,
    PLANNER_SYSTEM_PROMPT,
)
from multi_agent_system.planner.schemas import PlannedTask, PlannerOutput


class PlannerAgent:
    def __init__(self) -> None:
        self.llm = get_llm()
        self.structured_llm = None

    async def ainvoke(
        self,
        user_input: str,
        *,
        memory_context: str | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> PlannerOutput:
        try:
            output = await self._invoke_planner_once(
                user_input,
                memory_context=memory_context,
                conversation_messages=conversation_messages,
            )
            return self._normalize_output(output)

        except Exception as first_error:
            try:
                repaired_output = await self._repair_planner_output(
                    user_input=user_input,
                    error=first_error,
                    memory_context=memory_context,
                    conversation_messages=conversation_messages,
                )
                return self._normalize_output(repaired_output)

            except Exception as repair_error:
                return self._safe_failed_output(
                    user_input=user_input,
                    error=repair_error,
                )

    # Explain this code block
    async def _invoke_planner_once(
        self,
        user_input: str,
        *,
        memory_context: str | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> PlannerOutput:
        structured_llm = self._get_structured_llm()

        messages = [
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            *_memory_messages(memory_context),
            *_planner_request_messages(
                user_input,
                conversation_messages=conversation_messages,
            ),
        ]

        result = await ainvoke_with_optional_config(
            structured_llm,
            messages,
            config=trace_config(run_name="planner.llm", tags=["planner", "llm"]),
        )

        return self._coerce_planner_output(result)

    # TODO: if we dont need the build repair prompt, does this code block still usefull
    async def _repair_planner_output(
        self,
        *,
        user_input: str,
        error: Exception,
        memory_context: str | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> PlannerOutput:
        structured_llm = self._get_structured_llm()
        repair_prompt = self._build_repair_prompt(
            user_input=user_input,
            error=error,
        )

        messages = [
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            *_memory_messages(memory_context),
            *_conversation_messages(conversation_messages),
            HumanMessage(content=repair_prompt),
        ]

        result = await ainvoke_with_optional_config(
            structured_llm,
            messages,
            config=trace_config(run_name="planner.repair", tags=["planner", "llm"]),
        )

        return self._coerce_planner_output(result)

    # TODO: explain this code block
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

    # TODO: Don't understand this code block, why we have this and what is does
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

    # TODO: use the prompt.py only, not build random prompt repair
    def _build_repair_prompt(
        self,
        *,
        user_input: str,
        error: Exception,
    ) -> str:
        return PLANNER_REPAIR_PROMPT.format(
            user_input=user_input,
            error=error,
        )
    # TODO: explain why have safe fail ouput, if the planner failed, it should fail the whole system
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

    # TODO: Explain this code block
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


def _memory_messages(memory_context: str | None) -> list[SystemMessage]:
    if not memory_context:
        return []

    return [
        SystemMessage(
            content=(
                "Relevant sanitized memory skills:\n"
                f"{memory_context}\n\n"
                "Use these skills only as routing guidance. The current user "
                "request and planner rules take precedence. Do not invent "
                "missing values from memory."
            )
        )
    ]


def _planner_request_messages(
    user_input: str,
    *,
    conversation_messages: list[dict[str, str]] | None,
) -> list[BaseMessage]:
    conversation = _conversation_messages(conversation_messages)
    if conversation:
        return [
            SystemMessage(
                content=(
                    "Return a valid PlannerOutput for the latest user message "
                    "in the conversation. Use prior messages only to resolve "
                    "same-thread follow-ups, clarifications, and references. "
                    "Do not include explanations outside the structured output."
                )
            ),
            *conversation,
        ]

    return [
        HumanMessage(
            content=(
                "Return a valid PlannerOutput for the following request.\n"
                "Do not include explanations outside the structured output.\n\n"
                f"{user_input}"
            )
        )
    ]


def _conversation_messages(
    messages: list[dict[str, str]] | None,
) -> list[BaseMessage]:
    converted: list[BaseMessage] = []

    for message in messages or []:
        role = str(message.get("role") or "").strip().lower()
        content = str(message.get("content") or "").strip()
        if not content:
            continue

        if role == "user":
            converted.append(HumanMessage(content=content))
        elif role in {"assistant", "ai"}:
            converted.append(AIMessage(content=content))

    return converted
