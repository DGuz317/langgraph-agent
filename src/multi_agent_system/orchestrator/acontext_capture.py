from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Protocol

from acontext import AcontextAsyncClient
from acontext.errors import APIError, AcontextError

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
        """Store one user-visible planner interaction for skill learning."""


class AcontextCapture:
    """Store compact planner conversations for Acontext skill learning.

    LangSmith owns task and execution tracing. Acontext receives only the user
    turn and final assistant answer so it can generate reusable skills without
    running its dashboard task extractor.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        user_identifier: str,
        timeout: float = 2000.0,
        task_check_attempts: int = 6,
        task_check_interval: float = 0.5,
        client_factory: Callable[[], AcontextAsyncClient] | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._user_identifier = user_identifier
        self._timeout = timeout
        self._client_factory = client_factory or self._build_client
        self._learning_space_id: str | None = None
        self._attached_session_ids: set[str] = set()
        _ = (task_check_attempts, task_check_interval)

    async def capture(
        self,
        *,
        user_input: str,
        thread_id: str,
        resume: bool,
        response: PlannerServiceResponse,
    ) -> None:
        session_id = acontext_session_id(thread_id)

        try:
            async with self._client_factory() as client:
                space_id = await self._get_or_create_learning_space(client)
                await _ensure_session(
                    client,
                    session_id=session_id,
                    user_identifier=self._user_identifier,
                )
                await _store_learning_messages(
                    client,
                    session_id=session_id,
                    user_input=user_input,
                    resume=resume,
                    response=response,
                )

                if response.status == "completed":
                    await _flush_session(
                        client,
                        session_id=session_id,
                        thread_id=thread_id,
                    )
                    if session_id not in self._attached_session_ids:
                        await _ensure_learning_session(
                            client,
                            space_id=space_id,
                            session_id=session_id,
                            thread_id=thread_id,
                        )
                        self._attached_session_ids.add(session_id)
        except AcontextError as exc:
            logger.warning(
                "Acontext skill learning skipped for planner thread %s: %s",
                thread_id,
                exc,
            )

    async def _get_or_create_learning_space(self, client: AcontextAsyncClient) -> str:
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

    def _build_client(self) -> AcontextAsyncClient:
        return AcontextAsyncClient(
            api_key=self._api_key,
            base_url=self._base_url,
            timeout=self._timeout,
        )


def build_acontext_capture() -> PlannerInteractionCapture | None:
    """Build skill-learning capture only when explicitly enabled and configured."""
    if not settings.acontext_enabled:
        return None

    if not settings.acontext_api_key:
        logger.warning(
            "Acontext skill learning is enabled but ACONTEXT_API_KEY is unset; "
            "planner interactions will not be learned."
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
        "task_tracking": "disabled",
    }
    try:
        await client.sessions.create(
            user=user_identifier,
            disable_task_tracking=True,
            configs=configs,
            use_uuid=session_id,
        )
    except APIError as exc:
        if exc.status_code != 409:
            raise

        await client.sessions.update_configs(session_id, configs=configs)


async def _store_learning_messages(
    client: AcontextAsyncClient,
    *,
    session_id: str,
    user_input: str,
    resume: bool,
    response: PlannerServiceResponse,
) -> None:
    await client.sessions.store_message(
        session_id,
        blob={"role": "user", "content": user_input},
        format="openai",
        meta={
            "message_kind": "skill_learning_user_input",
            "resume": resume,
            "capture_policy": MEMORY_SCOPE,
        },
    )
    await client.sessions.store_message(
        session_id,
        blob={
            "role": "assistant",
            "content": _final_response_text(response),
        },
        format="openai",
        meta={
            "message_kind": "skill_learning_final_response",
            "planner_status": response.status,
            "capture_policy": MEMORY_SCOPE,
        },
    )


async def _flush_session(
    client: AcontextAsyncClient,
    *,
    session_id: str,
    thread_id: str,
) -> None:
    try:
        await client.sessions.flush(session_id)
    except AcontextError as exc:
        logger.warning(
            "Acontext skill learning skipped for planner thread %s: "
            "failed to flush session: %s",
            thread_id,
            exc,
        )
        raise


async def _ensure_learning_session(
    client: AcontextAsyncClient,
    *,
    space_id: str,
    session_id: str,
    thread_id: str,
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
        logger.debug(
            "Acontext skill learning already exists for planner thread %s.",
            thread_id,
        )


def _final_response_text(response: PlannerServiceResponse) -> str:
    if response.status == "interrupted":
        return (
            response.interrupt_message
            or "Additional information is required before the workflow can continue."
        )

    if response.status == "failed":
        return response.final_answer or "Planner workflow failed."

    return response.final_answer or "Planner workflow completed."
