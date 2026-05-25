from __future__ import annotations

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


class PlannerInteractionCapture(Protocol):
    async def capture(
        self,
        *,
        user_input: str,
        thread_id: str,
        resume: bool,
        response: PlannerServiceResponse,
    ) -> None:
        """Store one planner interaction."""


class AcontextCapture:
    """Capture user-visible planner turns in Acontext."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        user_identifier: str,
        client_factory: Callable[[], AcontextAsyncClient] | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._user_identifier = user_identifier
        self._client_factory = client_factory or self._build_client

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

        async with self._client_factory() as client:
            await _ensure_session(
                client,
                session_id=session_id,
                thread_id=thread_id,
                user_identifier=self._user_identifier,
            )
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

    def _build_client(self) -> AcontextAsyncClient:
        return AcontextAsyncClient(
            api_key=self._api_key,
            base_url=self._base_url,
        )


def build_acontext_capture() -> PlannerInteractionCapture | None:
    """Build runtime capture only when explicitly enabled and configured."""
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
    )


def acontext_session_id(thread_id: str) -> str:
    """Map existing planner thread identifiers into stable Acontext UUIDs."""
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
            },
            use_uuid=session_id,
        )
    except APIError as exc:
        if exc.status_code != 409:
            raise
