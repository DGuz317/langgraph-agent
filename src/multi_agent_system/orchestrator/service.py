from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from multi_agent_system.common.observability import trace_config
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
        capture_in_background: bool | None = None,
    ) -> None:
        self.graph = graph or planner_graph
        using_default_capture = capture is _DEFAULT_CAPTURE
        if capture is _DEFAULT_CAPTURE:
            from multi_agent_system.orchestrator.acontext_capture import (
                build_acontext_capture,
            )

            capture = build_acontext_capture()
        self.capture = capture
        self._capture_in_background = (
            using_default_capture
            if capture_in_background is None
            else capture_in_background
        )
        self._background_capture_tasks: set[asyncio.Task[None]] = set()
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
            resume: Deprecated compatibility flag. Conversation continuity is
                controlled by thread_id.

        Returns:
            PlannerServiceResponse with completed/interrupted/failed status.
        """
        active_thread_id = thread_id or str(uuid4())
        config = {
            "configurable": {
                "thread_id": active_thread_id,
            }
        }
        if resume is not None:
            logger.warning(
                "Ignoring deprecated resume=%s for planner thread %s; "
                "send thread_id with normal user_input for same-thread conversation.",
                resume,
                active_thread_id,
            )
        request_id = str(uuid4())
        config.update(
            trace_config(
                run_name="planner.invoke",
                thread_id=active_thread_id,
                request_id=request_id,
                tags=["planner", "api"],
            )
        )
        memory = await self._recall_memory(user_input, thread_id=active_thread_id)

        payload: dict[str, Any] = {"user_input": user_input}
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
                    status="completed",
                    thread_id=active_thread_id,
                    final_answer=_extract_interrupt_message(result),
                    interrupt_message=None,
                    needs_resume=False,
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
            resume=False,
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

        if self._capture_in_background:
            task = asyncio.create_task(
                self._capture_interaction_safely(
                    user_input=user_input,
                    thread_id=thread_id,
                    resume=resume,
                    response=response,
                )
            )
            self._background_capture_tasks.add(task)
            task.add_done_callback(self._background_capture_tasks.discard)
            return

        await self._capture_interaction_safely(
            user_input=user_input,
            thread_id=thread_id,
            resume=resume,
            response=response,
        )

    async def _capture_interaction_safely(
        self,
        *,
        user_input: str,
        thread_id: str,
        resume: bool,
        response: PlannerServiceResponse,
    ) -> None:
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
