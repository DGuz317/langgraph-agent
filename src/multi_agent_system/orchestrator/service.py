from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from langgraph.types import Command

from multi_agent_system.orchestrator.schemas import PlannerServiceResponse
from multi_agent_system.planner_app.graph import planner_graph

if TYPE_CHECKING:
    from multi_agent_system.orchestrator.acontext_capture import PlannerInteractionCapture
    from multi_agent_system.orchestrator.acontext_memory import PlannerMemoryRecall

logger = logging.getLogger(__name__)
_DEFAULT_CAPTURE = object()
_DEFAULT_MEMORY_RECALL = object()


class PlannerService:
    """Reusable runtime wrapper for planner graph invocation."""

    def __init__(
        self,
        graph: Any | None = None,
        capture: PlannerInteractionCapture | None | object = _DEFAULT_CAPTURE,
        memory_recall: PlannerMemoryRecall | None | object = _DEFAULT_MEMORY_RECALL,
    ) -> None:
        self.graph = graph or planner_graph
        if capture is _DEFAULT_CAPTURE:
            from multi_agent_system.orchestrator.acontext_capture import (
                build_acontext_capture,
            )

            capture = build_acontext_capture()
        self.capture = capture
        if memory_recall is _DEFAULT_MEMORY_RECALL:
            from multi_agent_system.orchestrator.acontext_memory import (
                build_acontext_memory_recall,
            )

            memory_recall = build_acontext_memory_recall()
        self.memory_recall = memory_recall

    async def invoke(
        self,
        user_input: str,
        *,
        thread_id: str | None = None,
        resume: bool | None = None,
    ) -> PlannerServiceResponse:
        """Invoke or resume the planner graph.

        Args:
            user_input: New user query, or HITL resume answer when resume=True.
            thread_id: Existing thread id for resume, or None for a new thread.
            resume: Whether to send user_input as Command(resume=...). When
                omitted, an existing interrupted thread is auto-resumed.

        Returns:
            PlannerServiceResponse with completed/interrupted/failed status.
        """
        active_thread_id = thread_id or str(uuid4())
        config = {
            "configurable": {
                "thread_id": active_thread_id,
            }
        }
        should_resume = await self._should_resume(
            thread_id=thread_id,
            active_thread_id=active_thread_id,
            resume=resume,
            config=config,
        )
        memory = await self._recall_memory(user_input, thread_id=active_thread_id)

        payload: Any
        if should_resume:
            payload = Command(resume=user_input)
        else:
            payload = {"user_input": user_input}
            if memory.context:
                payload["memory_context"] = memory.context

        try:
            result = await self.graph.ainvoke(payload, config=config)
        except Exception as exc:
            response = PlannerServiceResponse(
                status="failed",
                thread_id=active_thread_id,
                final_answer=f"System error: {exc}",
                raw_result={
                    "memory": memory.metadata,
                },
            )
        else:
            if _has_interrupt(result):
                response = PlannerServiceResponse(
                    status="interrupted",
                    thread_id=active_thread_id,
                    interrupt_message=_extract_interrupt_message(result),
                    needs_resume=True,
                    raw_result=_with_memory_metadata(
                        _safe_raw_result(result),
                        memory.metadata,
                    ),
                )
            else:
                response = PlannerServiceResponse(
                    status="completed",
                    thread_id=active_thread_id,
                    final_answer=_extract_final_answer(result),
                    needs_resume=False,
                    raw_result=_with_memory_metadata(
                        _safe_raw_result(result),
                        memory.metadata,
                    ),
                )

        await self._capture_interaction(
            user_input=user_input,
            thread_id=active_thread_id,
            resume=should_resume,
            response=response,
        )
        return response

    async def _should_resume(
        self,
        *,
        thread_id: str | None,
        active_thread_id: str,
        resume: bool | None,
        config: dict[str, Any],
    ) -> bool:
        if resume is True:
            if not thread_id:
                raise ValueError("resume=True requires an existing thread_id.")
            return True

        if resume is False or thread_id is None:
            return False

        aget_state = getattr(self.graph, "aget_state", None)
        if aget_state is None:
            return False

        try:
            snapshot = await aget_state(config)
        except Exception:
            logger.debug(
                "Unable to inspect planner thread %s for auto-resume.",
                active_thread_id,
                exc_info=True,
            )
            return False

        return bool(getattr(snapshot, "interrupts", ()))

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

    async def _recall_memory(self, user_input: str, *, thread_id: str):
        from multi_agent_system.orchestrator.acontext_memory import (
            disabled_memory_result,
            failed_memory_result,
        )

        if self.memory_recall is None:
            return disabled_memory_result()

        try:
            return await self.memory_recall.recall(user_input, thread_id=thread_id)
        except Exception:
            logger.exception("Planner memory recall failed; continuing without memory.")
            return failed_memory_result()


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
    """Return graph result without internal prompt-injection context.

    Kept as a helper so future API layers can sanitize non-JSON-serializable
    interrupt objects without changing PlannerService.invoke().
    """
    return {
        key: value
        for key, value in result.items()
        if key != "memory_context"
    }


def _with_memory_metadata(
    raw_result: dict[str, Any],
    memory_metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        **raw_result,
        "memory": memory_metadata,
    }
