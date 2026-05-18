from __future__ import annotations

from typing import Any
from uuid import uuid4

from langgraph.types import Command

from multi_agent_system.orchestrator.schemas import PlannerServiceResponse
from multi_agent_system.planner_app.graph import planner_graph


class PlannerService:
    """Reusable runtime wrapper for planner graph invocation."""

    def __init__(self, graph: Any | None = None) -> None:
        self.graph = graph or planner_graph

    async def invoke(
        self,
        user_input: str,
        *,
        thread_id: str | None = None,
        resume: bool = False,
    ) -> PlannerServiceResponse:
        """Invoke or resume the planner graph.

        Args:
            user_input: New user query, or HITL resume answer when resume=True.
            thread_id: Existing thread id for resume, or None for a new thread.
            resume: Whether to send user_input as Command(resume=...).

        Returns:
            PlannerServiceResponse with completed/interrupted/failed status.
        """
        active_thread_id = thread_id or str(uuid4())
        config = {
            "configurable": {
                "thread_id": active_thread_id,
            }
        }

        payload: Any
        if resume:
            payload = Command(resume=user_input)
        else:
            payload = {"user_input": user_input}

        try:
            result = await self.graph.ainvoke(payload, config=config)
        except Exception as exc:
            return PlannerServiceResponse(
                status="failed",
                thread_id=active_thread_id,
                final_answer=f"System error: {exc}",
                raw_result={},
            )

        if _has_interrupt(result):
            return PlannerServiceResponse(
                status="interrupted",
                thread_id=active_thread_id,
                interrupt_message=_extract_interrupt_message(result),
                needs_resume=True,
                raw_result=_safe_raw_result(result),
            )

        return PlannerServiceResponse(
            status="completed",
            thread_id=active_thread_id,
            final_answer=_extract_final_answer(result),
            needs_resume=False,
            raw_result=_safe_raw_result(result),
        )


def _has_interrupt(result: dict[str, Any]) -> bool:
    return "__interrupt__" in result


def _extract_interrupt_message(result: dict[str, Any]) -> str:
    interrupts = result.get("__interrupt__", [])

    if not interrupts:
        return "Could you provide the missing information?"

    first_interrupt = interrupts[0]
    value = getattr(first_interrupt, "value", first_interrupt)

    if isinstance(value, dict):
        question = value.get("question")
        if question:
            return str(question)

    return str(value)


def _extract_final_answer(result: dict[str, Any]) -> str:
    return (
        result.get("final_answer")
        or result.get("answer")
        or "I could not complete the request."
    )


def _safe_raw_result(result: dict[str, Any]) -> dict[str, Any]:
    """Return result as-is when possible.

    Kept as a helper so future API layers can sanitize non-JSON-serializable
    interrupt objects without changing PlannerService.invoke().
    """
    return result
