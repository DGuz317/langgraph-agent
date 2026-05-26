from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from langgraph.types import Command

from multi_agent_system.orchestrator.schemas import PlannerServiceResponse
from multi_agent_system.planner_app.graph import planner_graph

if TYPE_CHECKING:
    from multi_agent_system.orchestrator.acontext_capture import PlannerInteractionCapture

logger = logging.getLogger(__name__)
_DEFAULT_CAPTURE = object()


class PlannerService:
    """Reusable runtime wrapper for planner graph invocation."""

    def __init__(
        self,
        graph: Any | None = None,
        capture: PlannerInteractionCapture | None | object = _DEFAULT_CAPTURE,
    ) -> None:
        self.graph = graph or planner_graph
        if capture is _DEFAULT_CAPTURE:
            from multi_agent_system.orchestrator.acontext_capture import (
                build_acontext_capture,
            )

            capture = build_acontext_capture()
        self.capture = capture

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
            response = PlannerServiceResponse(
                status="failed",
                thread_id=active_thread_id,
                final_answer=f"System error: {exc}",
                raw_result={},
            )
        else:
            if _has_interrupt(result):
                response = PlannerServiceResponse(
                    status="interrupted",
                    thread_id=active_thread_id,
                    interrupt_message=_extract_interrupt_message(result),
                    needs_resume=True,
                    raw_result=_safe_raw_result(result),
                )
            else:
                response = PlannerServiceResponse(
                    status="completed",
                    thread_id=active_thread_id,
                    final_answer=_extract_final_answer(result),
                    needs_resume=False,
                    raw_result=_safe_raw_result(result),
                )

        await self._capture_interaction(
            user_input=user_input,
            thread_id=active_thread_id,
            resume=resume,
            response=response,
        )
        return response

    async def _capture_interaction(
        self,
        *,
        user_input: str,
        thread_id: str,
        resume: bool,
        response: PlannerServiceResponse,
    ) -> None:
        if self.capture is None:
            return

        try:
            await self.capture.capture(
                user_input=user_input,
                thread_id=thread_id,
                resume=resume,
                response=response,
            )
        except Exception:
            logger.exception(
                "Acontext capture failed for planner thread %s; continuing.",
                thread_id,
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
