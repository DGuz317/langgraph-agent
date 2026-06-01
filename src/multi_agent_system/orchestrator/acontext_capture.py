from __future__ import annotations

import asyncio
import json
import logging
import re
from collections.abc import Callable
from typing import Protocol

from acontext import AcontextAsyncClient
from acontext.errors import APIError, AcontextError

from multi_agent_system.common.execution_evidence import ExecutionEvidence
from multi_agent_system.config import settings
from multi_agent_system.orchestrator.acontext_common import (
    LEARNING_SPACE_META,
    MEMORY_SCOPE,
    acontext_session_id,
)
from multi_agent_system.orchestrator.schemas import PlannerServiceResponse

logger = logging.getLogger(__name__)


class PlannerInteractionCapture(Protocol):
    async def capture(
        self,
        *,
        user_input: str,
        thread_id: str,
        resume: bool,
        response: PlannerServiceResponse,
    ) -> None:
        """Store one user-visible planner interaction."""


class AcontextCapture:
    """Store planner conversations and attach them to one learning space."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        user_identifier: str,
        timeout: float = 1000.0,
        client_factory: Callable[[], AcontextAsyncClient] | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._user_identifier = user_identifier
        self._timeout = timeout
        self._client_factory = client_factory or self._build_client
        self._learning_space_id: str | None = None
        self._learning_space_lock = asyncio.Lock()
        self._attached_session_ids: set[str] = set()
        self._session_locks: dict[str, asyncio.Lock] = {}
        self._stored_evidence_signatures: dict[str, set[str]] = {}

    async def capture(
        self,
        *,
        user_input: str,
        thread_id: str,
        resume: bool,
        response: PlannerServiceResponse,
    ) -> None:
        session_id = acontext_session_id(thread_id)
        evidence = _extract_execution_evidence(response)

        try:
            async with self._session_lock(session_id):
                async with self._client_factory() as client:
                    space_id = await self._get_or_create_learning_space(client)
                    await _ensure_session(
                        client,
                        session_id=session_id,
                        user_identifier=self._user_identifier,
                    )

                    if session_id not in self._attached_session_ids:
                        await _ensure_learning_session(
                            client,
                            space_id=space_id,
                            session_id=session_id,
                        )
                        self._attached_session_ids.add(session_id)

                    await client.sessions.store_message(
                        session_id,
                        blob={"role": "user", "content": user_input},
                        format="openai",
                        meta={
                            "message_kind": "user_input",
                            "resume": resume,
                            "capture_policy": MEMORY_SCOPE,
                        },
                    )

                    await self._store_planner_trace(
                        client,
                        session_id=session_id,
                        response=response,
                        evidence=evidence,
                    )

                    await self._store_new_trace_messages(
                        client,
                        session_id=session_id,
                        evidence=evidence,
                    )

                    await client.sessions.store_message(
                        session_id,
                        blob={
                            "role": "assistant",
                            "content": _final_response_text(response),
                        },
                        format="openai",
                        meta={
                            "message_kind": "final_response",
                            "planner_status": response.status,
                            "capture_policy": MEMORY_SCOPE,
                        },
                    )

                    if response.status in {"completed", "failed"}:
                        await client.sessions.flush(session_id)
                        if _has_planner_tasks(response):
                            await _warn_if_no_acontext_tasks(
                                client,
                                session_id=session_id,
                                thread_id=thread_id,
                            )
        except AcontextError as exc:
            logger.warning(
                "Acontext capture skipped for planner thread %s: %s",
                thread_id,
                exc,
            )

    async def _store_planner_trace(
        self,
        client: AcontextAsyncClient,
        *,
        session_id: str,
        response: PlannerServiceResponse,
        evidence: list[ExecutionEvidence],
    ) -> None:
        trace = _planner_trace_text(response, evidence)
        if trace is None:
            return

        stored = self._stored_evidence_signatures.setdefault(session_id, set())
        signature = f"planner_trace:{trace}"
        if signature in stored:
            return

        await client.sessions.store_message(
            session_id,
            blob={"role": "assistant", "content": trace},
            format="openai",
            meta={
                "message_kind": "planner_trace",
                "capture_policy": MEMORY_SCOPE,
            },
        )
        stored.add(signature)

    async def _store_new_trace_messages(
        self,
        client: AcontextAsyncClient,
        *,
        session_id: str,
        evidence: list[ExecutionEvidence],
    ) -> None:
        stored = self._stored_evidence_signatures.setdefault(session_id, set())

        for item in evidence:
            signature = item.model_dump_json()
            if signature in stored:
                continue

            stored_message = await _store_trace_message(
                client,
                session_id=session_id,
                evidence=item,
            )
            if stored_message:
                stored.add(signature)

    async def _get_or_create_learning_space(self, client: AcontextAsyncClient) -> str:
        if self._learning_space_id is not None:
            return self._learning_space_id

        async with self._learning_space_lock:
            if self._learning_space_id is not None:
                return self._learning_space_id

            existing = await client.learning_spaces.list(
                user=self._user_identifier,
                limit=1,
                filter_by_meta=LEARNING_SPACE_META,
            )

            if existing.items:
                self._learning_space_id = existing.items[0].id
            else:
                created = await client.learning_spaces.create(
                    user=self._user_identifier,
                    meta=LEARNING_SPACE_META,
                )
                self._learning_space_id = created.id

        return self._learning_space_id

    def _session_lock(self, session_id: str) -> asyncio.Lock:
        lock = self._session_locks.get(session_id)
        if lock is None:
            lock = asyncio.Lock()
            self._session_locks[session_id] = lock
        return lock

    def _build_client(self) -> AcontextAsyncClient:
        return AcontextAsyncClient(
            api_key=self._api_key,
            base_url=self._base_url,
            timeout=self._timeout,
        )


def build_acontext_capture() -> PlannerInteractionCapture | None:
    """Build capture only when explicitly enabled and configured."""
    if not settings.acontext_enabled:
        return None

    if not settings.acontext_api_key:
        logger.warning(
            "Acontext capture is enabled but ACONTEXT_API_KEY is unset; "
            "planner interactions will not be captured."
        )
        return None

    return AcontextCapture(
        api_key=settings.acontext_api_key,
        base_url=settings.acontext_base_url,
        user_identifier=settings.acontext_user_identifier,
        timeout=settings.acontext_timeout,
    )


async def _ensure_session(
    client: AcontextAsyncClient,
    *,
    session_id: str,
    user_identifier: str,
) -> None:
    configs = {
        "source": "multi_agent_system.planner",
        "memory_scope": MEMORY_SCOPE,
        "capture_policy": MEMORY_SCOPE,
        "task_tracking": "enabled",
    }
    try:
        await client.sessions.create(
            user=user_identifier,
            disable_task_tracking=False,
            configs=configs,
            use_uuid=session_id,
        )
    except APIError as exc:
        if exc.status_code != 409:
            raise

        await client.sessions.update_configs(session_id, configs=configs)
        session = await client.sessions.get_configs(session_id)
        if session.disable_task_tracking:
            logger.warning(
                "Acontext session %s has disable_task_tracking=true; "
                "dashboard tasks will not be extracted for this session.",
                session_id,
            )


async def _ensure_learning_session(
    client: AcontextAsyncClient,
    *,
    space_id: str,
    session_id: str,
) -> None:
    try:
        await client.learning_spaces.get_session(space_id, session_id=session_id)
        return
    except APIError as exc:
        if exc.status_code != 404:
            raise

    try:
        await client.learning_spaces.learn(space_id, session_id=session_id)
    except APIError as exc:
        if exc.status_code != 409:
            raise


async def _warn_if_no_acontext_tasks(
    client: AcontextAsyncClient,
    *,
    session_id: str,
    thread_id: str,
) -> None:
    try:
        tasks = await client.sessions.get_tasks(session_id, limit=1)
    except AcontextError as exc:
        logger.debug(
            "Could not verify Acontext task extraction for planner thread %s: %s",
            thread_id,
            exc,
        )
        return

    if tasks.items:
        return

    logger.warning(
        "Acontext extracted no tasks for planner thread %s after flush. "
        "Check the Acontext Task Agent LLM/runtime if the dashboard shows No Task.",
        thread_id,
    )


def _extract_execution_evidence(
    response: PlannerServiceResponse,
) -> list[ExecutionEvidence]:
    values = response.raw_result.get("execution_evidence", [])
    if not isinstance(values, list):
        return []

    evidence: list[ExecutionEvidence] = []
    for value in values:
        try:
            evidence.append(ExecutionEvidence.model_validate(value))
        except ValueError:
            continue
    return evidence


def _has_planner_tasks(response: PlannerServiceResponse) -> bool:
    planner_output = response.raw_result.get("planner_output")
    if not isinstance(planner_output, dict):
        return False

    tasks = planner_output.get("tasks", [])
    return isinstance(tasks, list) and any(isinstance(task, dict) for task in tasks)


def _planner_trace_text(
    response: PlannerServiceResponse,
    evidence: list[ExecutionEvidence],
) -> str | None:
    planner_output = response.raw_result.get("planner_output")
    if not isinstance(planner_output, dict):
        return None

    tasks = planner_output.get("tasks", [])
    if not isinstance(tasks, list):
        return None

    if not tasks:
        return "Planner selected no executable invoice or music tasks."

    tool_progress = _tool_progress_by_agent(evidence)
    lines = [
        "Acontext task extraction summary:",
        f"- Overall status: {response.status}.",
    ]
    task_index = 0
    for task in tasks:
        if not isinstance(task, dict):
            continue

        task_index += 1
        agent = str(task.get("agent") or "unknown")
        status = str(task.get("status") or "not_started")
        details = [f"status: {status}"]

        instruction = _clean_text(task.get("instruction"))
        if instruction:
            details.append(f"instruction: {instruction}")

        progress = tool_progress.get(agent)
        if progress:
            details.append(f"progress: {', '.join(progress)}")

        lines.append(
            f"- Task {task_index}: {agent} agent should complete the instruction "
            f"({'; '.join(details)})"
        )

    if len(lines) == 2:
        return None

    return "\n".join(lines)


def _tool_progress_by_agent(
    evidence: list[ExecutionEvidence],
) -> dict[str, list[str]]:
    progress: dict[str, list[str]] = {}
    seen: set[tuple[str, str]] = set()

    for item in evidence:
        if item.kind != "mcp_tool_result" or item.status != "completed":
            continue

        key = (item.agent, item.operation)
        if key in seen:
            continue

        seen.add(key)
        progress.setdefault(item.agent, []).append(
            f"completed tool {item.operation}"
        )

    return progress


def _format_task_args(value: object) -> str:
    if not isinstance(value, dict) or not value:
        return ""

    pairs: list[str] = []
    for key, raw in list(value.items())[:8]:
        cleaned = _clean_text(raw)
        if cleaned:
            pairs.append(f"{key}={cleaned}")

    if len(value) > 8:
        pairs.append("...")

    return ", ".join(pairs)


def _clean_text(value: object, *, max_chars: int = 240) -> str:
    if value is None:
        return ""

    text = str(value).strip()
    if not text:
        return ""

    text = " ".join(text.split())
    if len(text) <= max_chars:
        return text

    return f"{text[: max_chars - 3]}..."


def _final_response_text(response: PlannerServiceResponse) -> str:
    if response.status == "interrupted":
        return (
            response.interrupt_message
            or "Additional information is required before the workflow can continue."
        )

    if response.status == "failed":
        return response.final_answer or "Planner workflow failed."

    return response.final_answer or "Planner workflow completed."


async def _store_trace_message(
    client: AcontextAsyncClient,
    *,
    session_id: str,
    evidence: ExecutionEvidence,
) -> bool:
    if evidence.kind == "planner_decision":
        return False

    if evidence.kind in {"hitl_request", "hitl_resume", "aggregation"}:
        return False

    meta = {
        "message_kind": "workflow_trace",
        "trace_kind": evidence.kind,
        "capture_policy": MEMORY_SCOPE,
    }

    if evidence.kind == "mcp_tool_call" and evidence.call_id is not None:
        await client.sessions.store_message(
            session_id,
            blob={
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": evidence.call_id,
                        "type": "function",
                        "function": {
                            "name": _safe_tool_name(evidence),
                            "arguments": json.dumps(
                                _tool_call_arguments(evidence),
                                ensure_ascii=False,
                                default=str,
                            ),
                        },
                    }
                ],
            },
            format="openai",
            meta=meta,
        )
        return True

    if evidence.kind == "mcp_tool_result" and evidence.call_id is not None:
        await client.sessions.store_message(
            session_id,
            blob={
                "role": "tool",
                "tool_call_id": evidence.call_id,
                "content": evidence.summary,
            },
            format="openai",
            meta=meta,
        )
        return True

    if evidence.kind == "agent_result":
        return False

    return False


def _tool_call_arguments(evidence: ExecutionEvidence) -> dict[str, object]:
    if evidence.arguments:
        return evidence.arguments

    return {"fields": evidence.fields}


def _safe_tool_name(evidence: ExecutionEvidence) -> str:
    name = f"{evidence.agent}_{evidence.operation}"
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name)
