from types import SimpleNamespace

import pytest

from multi_agent_system.orchestrator.acontext_common import (
    MEMORY_SCOPE,
    acontext_session_id,
)
from multi_agent_system.orchestrator.acontext_memory import AcontextMemoryRecall


class FakeLearningSpaces:
    def __init__(
        self,
        *,
        space_id: str | None = "space-1",
        skills=None,
        wait_error: Exception | None = None,
        wait_status: str = "completed",
    ) -> None:
        self.space_id = space_id
        self.skills = skills or []
        self.wait_error = wait_error
        self.wait_status = wait_status
        self.list_calls = []
        self.list_skills_calls = []
        self.wait_for_learning_calls = []

    async def list(self, **kwargs):
        self.list_calls.append(kwargs)
        items = [SimpleNamespace(id=self.space_id)] if self.space_id else []
        return SimpleNamespace(items=items)

    async def list_skills(self, space_id: str):
        self.list_skills_calls.append(space_id)
        return self.skills

    async def wait_for_learning(self, space_id: str, **kwargs):
        self.wait_for_learning_calls.append((space_id, kwargs))
        if self.wait_error is not None:
            raise self.wait_error
        return SimpleNamespace(status=self.wait_status)


class FakeSkills:
    def __init__(self, files=None, error: Exception | None = None) -> None:
        self.files = files or {}
        self.error = error
        self.get_file_calls = []

    async def get_file(self, *, skill_id: str, file_path: str):
        self.get_file_calls.append((skill_id, file_path))
        if self.error is not None:
            raise self.error
        return SimpleNamespace(
            content=SimpleNamespace(
                raw=self.files.get((skill_id, file_path), ""),
            )
        )


class FakeClient:
    def __init__(
        self,
        *,
        space_id: str | None = "space-1",
        skills=None,
        files=None,
        error: Exception | None = None,
        wait_error: Exception | None = None,
        wait_status: str = "completed",
    ) -> None:
        self.learning_spaces = FakeLearningSpaces(
            space_id=space_id,
            skills=skills,
            wait_error=wait_error,
            wait_status=wait_status,
        )
        self.skills = FakeSkills(files=files, error=error)

    async def __aenter__(self):
        if isinstance(self.learning_spaces, Exception):
            raise self.learning_spaces
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None


def _skill(
    *,
    skill_id: str,
    name: str,
    description: str,
    updated_at: str = "2026-05-28T00:00:00Z",
):
    return SimpleNamespace(
        id=skill_id,
        name=name,
        description=description,
        updated_at=updated_at,
        file_index=[
            SimpleNamespace(path="SKILL.md", mime="text/markdown"),
        ],
    )


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_acontext_memory_recall_returns_relevant_sanitized_skill() -> None:
    skill = _skill(
        skill_id="skill-1",
        name="invoice-routing",
        description="Route invoice requests with customer_id to invoice workflows.",
    )
    client = FakeClient(
        skills=[skill],
        files={
            (
                "skill-1",
                "SKILL.md",
            ): "Use latest_invoice when the user asks for the latest invoice.",
        },
    )
    recall = AcontextMemoryRecall(
        api_key="test-key",
        base_url="https://example.test/api/v1",
        user_identifier="planner-service",
        client_factory=lambda: client,
    )

    result = await recall.recall("Get my latest invoice")

    assert "invoice-routing" in result.context
    assert "latest_invoice" in result.context
    assert result.metadata == {
        "recall_enabled": True,
        "recall_status": "ok",
        "skills_used": 1,
        "skill_names": ["invoice-routing"],
    }
    assert client.learning_spaces.list_calls == [
        {
            "user": "planner-service",
            "limit": 1,
            "filter_by_meta": {
                "source": "multi_agent_system.planner",
                "memory_scope": MEMORY_SCOPE,
            },
        }
    ]
    assert client.learning_spaces.wait_for_learning_calls == []


@pytest.mark.anyio
async def test_acontext_memory_recall_waits_for_thread_learning_before_skills() -> None:
    skill = _skill(
        skill_id="skill-1",
        name="invoice-routing",
        description="Route invoice requests.",
    )
    client = FakeClient(
        skills=[skill],
        files={
            ("skill-1", "SKILL.md"): "invoice skill",
        },
    )
    recall = AcontextMemoryRecall(
        api_key="test-key",
        base_url="https://example.test/api/v1",
        user_identifier="planner-service",
        client_factory=lambda: client,
    )

    result = await recall.recall("invoice", thread_id="thread-1")

    assert result.metadata["recall_status"] == "ok"
    assert client.learning_spaces.wait_for_learning_calls == [
        (
            "space-1",
            {
                "session_id": acontext_session_id("thread-1"),
                "timeout": 3.0,
                "poll_interval": 0.5,
            },
        )
    ]
    assert client.learning_spaces.list_skills_calls == ["space-1"]


@pytest.mark.anyio
async def test_acontext_memory_recall_continues_when_learning_wait_fails() -> None:
    skill = _skill(
        skill_id="skill-1",
        name="invoice-routing",
        description="Route invoice requests.",
    )
    client = FakeClient(
        skills=[skill],
        files={
            ("skill-1", "SKILL.md"): "invoice skill",
        },
        wait_error=TimeoutError("learning timeout"),
    )
    recall = AcontextMemoryRecall(
        api_key="test-key",
        base_url="https://example.test/api/v1",
        user_identifier="planner-service",
        client_factory=lambda: client,
    )

    result = await recall.recall("invoice", thread_id="thread-timeout")

    assert result.metadata["recall_status"] == "ok"
    assert result.metadata["skill_names"] == ["invoice-routing"]


@pytest.mark.anyio
async def test_acontext_memory_recall_uses_configured_short_learning_wait() -> None:
    client = FakeClient()
    recall = AcontextMemoryRecall(
        api_key="test-key",
        base_url="https://example.test/api/v1",
        user_identifier="planner-service",
        learning_wait_timeout=1.25,
        learning_wait_poll=0.25,
        client_factory=lambda: client,
    )

    result = await recall.recall("invoice", thread_id="thread-short-wait")

    assert result.metadata["recall_status"] == "empty"
    assert client.learning_spaces.wait_for_learning_calls == [
        (
            "space-1",
            {
                "session_id": acontext_session_id("thread-short-wait"),
                "timeout": 1.25,
                "poll_interval": 0.25,
            },
        )
    ]


@pytest.mark.anyio
async def test_acontext_memory_recall_can_skip_learning_wait() -> None:
    client = FakeClient()
    recall = AcontextMemoryRecall(
        api_key="test-key",
        base_url="https://example.test/api/v1",
        user_identifier="planner-service",
        learning_wait_timeout=0,
        client_factory=lambda: client,
    )

    result = await recall.recall("invoice", thread_id="thread-no-wait")

    assert result.metadata["recall_status"] == "empty"
    assert client.learning_spaces.wait_for_learning_calls == []


@pytest.mark.anyio
async def test_acontext_memory_recall_empty_when_no_learning_space() -> None:
    client = FakeClient(space_id=None)
    recall = AcontextMemoryRecall(
        api_key="test-key",
        base_url="https://example.test/api/v1",
        user_identifier="planner-service",
        client_factory=lambda: client,
    )

    result = await recall.recall("Get my latest invoice")

    assert result.context is None
    assert result.metadata["recall_status"] == "empty"


@pytest.mark.anyio
async def test_acontext_memory_recall_failed_when_client_errors() -> None:
    class FailingClient:
        async def __aenter__(self):
            raise RuntimeError("server down")

        async def __aexit__(self, exc_type, exc, tb):
            return None

    recall = AcontextMemoryRecall(
        api_key="test-key",
        base_url="https://example.test/api/v1",
        user_identifier="planner-service",
        client_factory=lambda: FailingClient(),
    )

    result = await recall.recall("Get my latest invoice")

    assert result.context is None
    assert result.metadata == {
        "recall_enabled": True,
        "recall_status": "failed",
        "skills_used": 0,
        "skill_names": [],
    }


@pytest.mark.anyio
async def test_acontext_memory_recall_respects_text_limit() -> None:
    skill = _skill(
        skill_id="skill-1",
        name="invoice-routing",
        description="invoice invoice invoice",
    )
    client = FakeClient(
        skills=[skill],
        files={
            ("skill-1", "SKILL.md"): "invoice " * 100,
        },
    )
    recall = AcontextMemoryRecall(
        api_key="test-key",
        base_url="https://example.test/api/v1",
        user_identifier="planner-service",
        max_chars=40,
        client_factory=lambda: client,
    )

    result = await recall.recall("invoice")

    assert len(result.context) <= 40
    assert result.context.endswith("[truncated]")


@pytest.mark.anyio
async def test_acontext_memory_recall_uses_injected_skill_selector() -> None:
    invoice_skill = _skill(
        skill_id="skill-1",
        name="invoice-routing",
        description="Route invoice requests.",
    )
    music_skill = _skill(
        skill_id="skill-2",
        name="music-routing",
        description="Route music requests.",
    )
    client = FakeClient(
        skills=[invoice_skill, music_skill],
        files={
            ("skill-1", "SKILL.md"): "invoice skill",
            ("skill-2", "SKILL.md"): "music skill",
        },
    )

    async def fake_selector(user_input, candidates, limit):
        assert user_input == "Get invoice information"
        assert limit == 3
        return [candidates[1]]

    recall = AcontextMemoryRecall(
        api_key="test-key",
        base_url="https://example.test/api/v1",
        user_identifier="planner-service",
        client_factory=lambda: client,
        skill_selector=fake_selector,
    )

    result = await recall.recall("Get invoice information")

    assert "music-routing" in result.context
    assert "invoice-routing" not in result.context
    assert result.metadata["skill_names"] == ["music-routing"]
