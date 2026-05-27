from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Protocol
from uuid import UUID, uuid5

from acontext import AcontextAsyncClient
from acontext.errors import APIError

from multi_agent_system.config import settings
from multi_agent_system.orchestrator.schemas import PlannerServiceResponse

logger = logging.getLogger(__name__)

_SESSION_NAMESPACE = UUID("cfcd8caa-f533-5ccd-a31c-c695f4f52142")
_LEARNING_SPACE_META = {
    "source": "multi_agent_system.planner",
    "memory_scope": "visible-chat-v1",
}


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

    async def capture(
        self,
        *,
        user_input: str,
        thread_id: str,
        resume: bool,
        response: PlannerServiceResponse,
    ) -> None:
        session_id = acontext_session_id(thread_id)
        assistant_text = response.interrupt_message or response.final_answer or ""

        async with self._session_lock(session_id):
            async with self._client_factory() as client:
                space_id = await self._get_or_create_learning_space(client)
                await _ensure_session(
                    client,
                    session_id=session_id,
                    thread_id=thread_id,
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
                        "planner_thread_id": thread_id,
                        "resume": resume,
                    },
                )
                await client.sessions.store_message(
                    session_id,
                    blob={"role": "assistant", "content": assistant_text},
                    format="openai",
                    meta={
                        "planner_thread_id": thread_id,
                        "planner_status": response.status,
                    },
                )

                if response.status in {"completed", "failed"}:
                    await client.sessions.flush(session_id)

    async def _get_or_create_learning_space(self, client: AcontextAsyncClient) -> str:
        if self._learning_space_id is not None:
            return self._learning_space_id

        async with self._learning_space_lock:
            if self._learning_space_id is not None:
                return self._learning_space_id

            existing = await client.learning_spaces.list(
                user=self._user_identifier,
                limit=1,
                filter_by_meta=_LEARNING_SPACE_META,
            )

            if existing.items:
                self._learning_space_id = existing.items[0].id
            else:
                created = await client.learning_spaces.create(
                    user=self._user_identifier,
                    meta=_LEARNING_SPACE_META,
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
    return str(uuid5(_SESSION_NAMESPACE, f"planner:{thread_id}"))


async def _ensure_session(
    client: AcontextAsyncClient,
    *,
    session_id: str,
    thread_id: str,
    user_identifier: str,
) -> None:
    try:
        await client.sessions.create(
            user=user_identifier,
            configs={
                "source": "multi_agent_system.planner",
                "planner_thread_id": thread_id,
                "memory_scope": "visible-chat-v1",
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
