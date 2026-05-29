from types import SimpleNamespace

import pytest

from multi_agent_system.orchestrator.acontext_memory import AcontextMemoryRecall


class FakeLearningSpaces:
    def __init__(self, *, space_id: str | None = "space-1", skills=None) -> None:
        self.space_id = space_id
        self.skills = skills or []
        self.list_calls = []
        self.list_skills_calls = []

    async def list(self, **kwargs):
        self.list_calls.append(kwargs)
        items = [SimpleNamespace(id=self.space_id)] if self.space_id else []
        return SimpleNamespace(items=items)

    async def list_skills(self, space_id: str):
        self.list_skills_calls.append(space_id)
        return self.skills


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
    ) -> None:
        self.learning_spaces = FakeLearningSpaces(
            space_id=space_id,
            skills=skills,
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
    }
    assert client.learning_spaces.list_calls == [
        {
            "user": "planner-service",
            "limit": 1,
            "filter_by_meta": {
                "source": "multi_agent_system.planner",
                "memory_scope": "sanitized-execution-v1",
            },
        }
    ]


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
