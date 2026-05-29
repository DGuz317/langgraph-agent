from __future__ import annotations

import asyncio
import json
import logging
import re
from collections.abc import Callable
from typing import Protocol
from uuid import UUID, uuid5

from acontext import AcontextAsyncClient
from acontext.errors import APIError

from multi_agent_system.common.execution_evidence import ExecutionEvidence
from multi_agent_system.config import settings
from multi_agent_system.orchestrator.acontext_memory import (
    LEARNING_SPACE_META,
    MEMORY_SCOPE,
)
from multi_agent_system.orchestrator.schemas import PlannerServiceResponse

logger = logging.getLogger(__name__)

_SESSION_NAMESPACE = UUID("cfcd8caa-f533-5ccd-a31c-c695f4f52142")


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
        evidence.extend(_interaction_evidence(response=response, evidence=evidence))
        user_text = _summarize_user_turn(resume=resume, evidence=evidence)
        assistant_text = _summarize_assistant_turn(response=response, evidence=evidence)

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
                    blob={"role": "user", "content": user_text},
                    format="openai",
                    meta={
                        "resume": resume,
                        "capture_policy": MEMORY_SCOPE,
                    },
                )

                await self._store_new_evidence(
                    client,
                    session_id=session_id,
                    evidence=evidence,
                )

                await client.sessions.store_message(
                    session_id,
                    blob={"role": "assistant", "content": assistant_text},
                    format="openai",
                    meta={
                        "planner_status": response.status,
                        "capture_policy": MEMORY_SCOPE,
                    },
                )

                if response.status in {"completed", "failed"}:
                    await client.sessions.flush(session_id)

    async def _store_new_evidence(
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

            await _store_evidence_message(
                client,
                session_id=session_id,
                evidence=item,
            )
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


def acontext_session_id(thread_id: str) -> str:
    """Map a LangGraph thread id into a stable Acontext UUID."""
    return str(uuid5(_SESSION_NAMESPACE, f"planner:{MEMORY_SCOPE}:{thread_id}"))


async def _ensure_session(
    client: AcontextAsyncClient,
    *,
    session_id: str,
    user_identifier: str,
) -> None:
    try:
        await client.sessions.create(
            user=user_identifier,
            configs={
                "source": "multi_agent_system.planner",
                "memory_scope": MEMORY_SCOPE,
                "capture_policy": MEMORY_SCOPE,
            },
            use_uuid=session_id,
        )
    except APIError as exc:
        if exc.status_code != 409:
            raise


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


def _summarize_user_turn(
    *,
    resume: bool,
    evidence: list[ExecutionEvidence],
) -> str:
    fields = _field_names(evidence)
    if resume:
        if fields:
            return (
                f"Supplied required fields: {', '.join(fields)}. "
                "Values omitted from memory."
            )
        return "Supplied requested follow-up information. Value omitted from memory."

    operations = _operations(evidence, kind="planner_decision")
    if operations and operations != ["no_task"]:
        return (
            f"Requested workflow: {', '.join(operations)}. "
            "Supplied values omitted from memory."
        )
    return "Submitted a planner request. User content omitted from memory."


def _interaction_evidence(
    *,
    response: PlannerServiceResponse,
    evidence: list[ExecutionEvidence],
) -> list[ExecutionEvidence]:
    if response.status != "interrupted":
        return []

    return [
        ExecutionEvidence(
            kind="hitl_request",
            agent="planner",
            operation="required_fields",
            status="interrupted",
            fields=_field_names(evidence),
            summary="Additional required fields requested; values omitted from memory.",
        )
    ]


def _summarize_assistant_turn(
    *,
    response: PlannerServiceResponse,
    evidence: list[ExecutionEvidence],
) -> str:
    fields = _field_names(evidence)
    if response.status == "interrupted":
        if fields:
            return f"Additional required fields requested: {', '.join(fields)}."
        return "Additional information was requested."

    if response.status == "failed":
        return "Planner workflow failed. Failure details omitted from memory."

    operations = _operations(evidence, kind="agent_result")
    if operations:
        return (
            f"Workflow completed successfully: {', '.join(operations)}. "
            "Returned values omitted from memory."
        )
    return "Planner workflow completed. Returned content omitted from memory."


def _field_names(evidence: list[ExecutionEvidence]) -> list[str]:
    return sorted(
        {
            field
            for item in evidence
            for field in item.fields
        }
    )


def _operations(
    evidence: list[ExecutionEvidence],
    *,
    kind: str,
) -> list[str]:
    return list(
        dict.fromkeys(
            item.operation
            for item in evidence
            if item.kind == kind
        )
    )


async def _store_evidence_message(
    client: AcontextAsyncClient,
    *,
    session_id: str,
    evidence: ExecutionEvidence,
) -> None:
    meta = {
        "evidence_kind": evidence.kind,
        "capture_policy": MEMORY_SCOPE,
    }

    if evidence.kind == "mcp_tool_call" and evidence.call_id is not None:
        await client.sessions.store_message(
            session_id,
            blob={
                "role": "assistant",
                "content": evidence.summary,
                "tool_calls": [
                    {
                        "id": evidence.call_id,
                        "type": "function",
                        "function": {
                            "name": _safe_tool_name(evidence),
                            "arguments": json.dumps({"fields": evidence.fields}),
                        },
                    }
                ],
            },
            format="openai",
            meta=meta,
        )
        return

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
        return

    await client.sessions.store_message(
        session_id,
        blob={"role": "assistant", "content": evidence.summary},
        format="openai",
        meta=meta,
    )


def _safe_tool_name(evidence: ExecutionEvidence) -> str:
    name = f"{evidence.agent}_{evidence.operation}"
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name)
