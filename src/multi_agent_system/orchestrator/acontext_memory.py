from __future__ import annotations

import logging
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal, Protocol

from acontext import AcontextAsyncClient
from acontext.errors import APIError, AcontextError
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from multi_agent_system.common.llm import get_llm
from multi_agent_system.config import settings
from multi_agent_system.orchestrator.acontext_common import (
    LEARNING_SPACE_META,
    MEMORY_SCOPE,
    acontext_session_id,
)

logger = logging.getLogger(__name__)

RecallStatus = Literal["disabled", "ok", "empty", "failed"]
DEFAULT_LEARNING_WAIT_TIMEOUT_SECONDS = 3.0
DEFAULT_LEARNING_WAIT_POLL_SECONDS = 0.5


@dataclass(frozen=True)
class MemoryRecallResult:
    context: str | None
    metadata: dict[str, Any]


class PlannerMemoryRecall(Protocol):
    async def recall(
        self,
        user_input: str,
        *,
        thread_id: str | None = None,
    ) -> MemoryRecallResult:
        """Return sanitized memory guidance for one planner request."""


class SkillSelection(BaseModel):
    indexes: list[int] = Field(
        default_factory=list,
        description="Zero-based indexes of relevant candidate skills.",
    )


SkillSelector = Callable[
    [str, list[dict[str, str]], int],
    Any,
]


class AcontextMemoryRecall:
    """Retrieve sanitized Acontext skills for planner guidance."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        user_identifier: str,
        limit: int = 3,
        max_chars: int = 3000,
        timeout: float = 1000.0,
        learning_wait_timeout: float = DEFAULT_LEARNING_WAIT_TIMEOUT_SECONDS,
        learning_wait_poll: float = DEFAULT_LEARNING_WAIT_POLL_SECONDS,
        client_factory: Callable[[], AcontextAsyncClient] | None = None,
        skill_selector: SkillSelector | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._user_identifier = user_identifier
        self._limit = max(0, limit)
        self._max_chars = max(0, max_chars)
        self._timeout = timeout
        self._learning_wait_timeout = max(0.0, learning_wait_timeout)
        self._learning_wait_poll = max(0.0, learning_wait_poll)
        self._client_factory = client_factory or self._build_client
        self._skill_selector = skill_selector or _select_relevant_skills

    async def recall(
        self,
        user_input: str,
        *,
        thread_id: str | None = None,
    ) -> MemoryRecallResult:
        if self._limit == 0 or self._max_chars == 0:
            return MemoryRecallResult(
                context=None,
                metadata=_memory_metadata("empty", skills_used=0),
            )

        try:
            async with self._client_factory() as client:
                space_id = await self._find_learning_space(client)
                if space_id is None:
                    return MemoryRecallResult(
                        context=None,
                        metadata=_memory_metadata("empty", skills_used=0),
                    )

                if thread_id is not None:
                    await self._wait_for_learning(client, space_id, thread_id)

                skills = await client.learning_spaces.list_skills(space_id)
                candidates = [
                    await self._skill_candidate(client, skill)
                    for skill in skills
                ]
                selected = await _call_skill_selector(
                    self._skill_selector,
                    user_input,
                    candidates,
                    self._limit,
                )

                if not selected:
                    return MemoryRecallResult(
                        context=None,
                        metadata=_memory_metadata("empty", skills_used=0),
                    )

                context = _format_memory_context(
                    selected,
                    max_chars=self._max_chars,
                )
                return MemoryRecallResult(
                    context=context,
                    metadata=_memory_metadata(
                        "ok",
                        skills_used=len(selected),
                        skill_names=_skill_names(selected),
                    ),
                )
        except Exception:
            logger.exception("Acontext recall failed; continuing without memory.")
            return MemoryRecallResult(
                context=None,
                metadata=_memory_metadata("failed", skills_used=0),
            )

    async def _find_learning_space(self, client: AcontextAsyncClient) -> str | None:
        spaces = await client.learning_spaces.list(
            user=self._user_identifier,
            limit=1,
            filter_by_meta=LEARNING_SPACE_META,
        )

        if not spaces.items:
            return None

        return spaces.items[0].id

    async def _wait_for_learning(
        self,
        client: AcontextAsyncClient,
        space_id: str,
        thread_id: str,
    ) -> None:
        session_id = acontext_session_id(thread_id)
        if self._learning_wait_timeout == 0:
            logger.debug(
                "Acontext learning wait disabled for planner thread %s.",
                thread_id,
            )
            return

        try:
            learning = await client.learning_spaces.wait_for_learning(
                space_id,
                session_id=session_id,
                timeout=self._learning_wait_timeout,
                poll_interval=self._learning_wait_poll,
            )
        except APIError as exc:
            if exc.status_code == 404:
                logger.debug(
                    "No Acontext learning session exists for planner thread %s.",
                    thread_id,
                )
                return
            logger.warning(
                "Acontext learning wait failed for planner thread %s: %s",
                thread_id,
                exc,
            )
            return
        except (TimeoutError, AcontextError) as exc:
            logger.warning(
                "Acontext learning wait skipped for planner thread %s: %s",
                thread_id,
                exc,
            )
            return

        status = str(getattr(learning, "status", "") or "").lower()
        if "failed" in status:
            logger.warning(
                "Acontext learning finished with failed status for planner thread %s.",
                thread_id,
            )

    async def _skill_candidate(
        self,
        client: AcontextAsyncClient,
        skill: Any,
    ) -> dict[str, str]:
        name = str(getattr(skill, "name", "") or "")
        description = str(getattr(skill, "description", "") or "")
        content = await _get_skill_markdown(client, skill)
        return {
            "name": name,
            "description": description,
            "content": content,
            "updated_at": str(getattr(skill, "updated_at", "") or ""),
        }

    def _build_client(self) -> AcontextAsyncClient:
        return AcontextAsyncClient(
            api_key=self._api_key,
            base_url=self._base_url,
            timeout=self._timeout,
        )


def build_acontext_memory_recall() -> PlannerMemoryRecall | None:
    """Build Acontext recall only when explicitly enabled and configured."""
    if not settings.acontext_recall_enabled:
        return None

    if not settings.acontext_api_key:
        logger.warning(
            "Acontext recall is enabled but ACONTEXT_API_KEY is unset; "
            "planner memory recall will be marked failed."
        )
        return _FailedMemoryRecall()

    return AcontextMemoryRecall(
        api_key=settings.acontext_api_key,
        base_url=settings.acontext_base_url,
        user_identifier=settings.acontext_user_identifier,
        limit=settings.acontext_recall_limit,
        max_chars=settings.acontext_recall_max_chars,
        timeout=settings.acontext_timeout,
        skill_selector=_llm_select_relevant_skills,
        learning_wait_timeout=settings.acontext_learning_wait_timeout,
        learning_wait_poll=settings.acontext_learning_wait_poll,
    )


def disabled_memory_result() -> MemoryRecallResult:
    return MemoryRecallResult(
        context=None,
        metadata={
            "recall_enabled": False,
            "recall_status": "disabled",
            "skills_used": 0,
            "skill_names": [],
        },
    )


def failed_memory_result() -> MemoryRecallResult:
    return MemoryRecallResult(
        context=None,
        metadata=_memory_metadata("failed", skills_used=0),
    )


class _FailedMemoryRecall:
    async def recall(
        self,
        user_input: str,
        *,
        thread_id: str | None = None,
    ) -> MemoryRecallResult:
        return failed_memory_result()


async def _get_skill_markdown(client: AcontextAsyncClient, skill: Any) -> str:
    for file_info in getattr(skill, "file_index", []) or []:
        path = str(getattr(file_info, "path", "") or "")
        if not path.lower().endswith(".md"):
            continue

        try:
            file_resp = await client.skills.get_file(
                skill_id=skill.id,
                file_path=path,
            )
        except Exception:
            logger.debug("Unable to read Acontext skill file %s.", path, exc_info=True)
            continue

        content = getattr(file_resp, "content", None)
        raw = getattr(content, "raw", None)
        if raw:
            return str(raw)

    return ""


async def _call_skill_selector(
    selector: SkillSelector,
    user_input: str,
    candidates: list[dict[str, str]],
    limit: int,
) -> list[dict[str, str]]:
    result = selector(user_input, candidates, limit)
    if hasattr(result, "__await__"):
        result = await result
    return list(result)


async def _llm_select_relevant_skills(
    user_input: str,
    candidates: list[dict[str, str]],
    limit: int,
) -> list[dict[str, str]]:
    if not candidates or limit <= 0:
        return []

    try:
        structured_llm = get_llm().with_structured_output(SkillSelection)
        candidate_text = "\n\n".join(
            f"[{index}] {candidate['name']}: {candidate['description']}\n"
            f"{_compact(candidate['content'])[:800]}"
            for index, candidate in enumerate(candidates)
        )
        result = await structured_llm.ainvoke(
            [
                SystemMessage(
                    content=(
                        "Select sanitized memory skills that help route the "
                        "current invoice/music planner request. Return only "
                        "candidate indexes. Do not select skills that would "
                        "invent missing user values."
                    )
                ),
                HumanMessage(
                    content=(
                        f"User request:\n{user_input}\n\n"
                        f"Max skills: {limit}\n\n"
                        f"Candidate skills:\n{candidate_text}"
                    )
                ),
            ]
        )
        selection = (
            result
            if isinstance(result, SkillSelection)
            else SkillSelection.model_validate(result)
        )
        selected = []
        for index in selection.indexes:
            if 0 <= index < len(candidates):
                selected.append(candidates[index])
            if len(selected) >= limit:
                break
        return selected
    except Exception:
        logger.exception(
            "Acontext LLM skill selection failed; falling back to lexical selection."
        )
        return _select_relevant_skills(user_input, candidates, limit)


def _select_relevant_skills(
    user_input: str,
    candidates: list[dict[str, str]],
    limit: int,
) -> list[dict[str, str]]:
    terms = _tokens(user_input)
    scored: list[tuple[int, dict[str, str]]] = []

    for candidate in candidates:
        text = " ".join(
            [
                candidate["name"],
                candidate["description"],
                candidate["content"],
            ]
        ).lower()
        score = sum(1 for term in terms if term in text)
        if score > 0:
            scored.append((score, candidate))

    scored.sort(
        key=lambda item: (
            item[0],
            item[1]["updated_at"],
        ),
        reverse=True,
    )

    return [candidate for _, candidate in scored[:limit]]


def _format_memory_context(
    candidates: list[dict[str, str]],
    *,
    max_chars: int,
) -> str:
    chunks = []
    for candidate in candidates:
        parts = [
            f"- {candidate['name']}: {candidate['description']}".strip(),
            _compact(candidate["content"]),
        ]
        chunks.append("\n".join(part for part in parts if part))

    text = "\n\n".join(chunks)
    if len(text) <= max_chars:
        return text

    return text[: max(0, max_chars - 14)].rstrip() + "\n[truncated]"


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z0-9_]+", text.lower())
        if len(token) >= 3
    }


def _compact(text: str) -> str:
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def _skill_names(candidates: list[dict[str, str]]) -> list[str]:
    return [candidate["name"] for candidate in candidates if candidate["name"]]


def _memory_metadata(
    status: RecallStatus,
    *,
    skills_used: int,
    skill_names: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "recall_enabled": True,
        "recall_status": status,
        "skills_used": skills_used,
        "skill_names": skill_names or [],
    }
