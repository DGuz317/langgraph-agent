from types import SimpleNamespace

import pytest

from acontext.errors import APIError, TransportError

from multi_agent_system.config import settings
from multi_agent_system.orchestrator.acontext_capture import (
    AcontextCapture,
    acontext_session_id,
    build_acontext_capture,
)
from multi_agent_system.orchestrator.acontext_common import MEMORY_SCOPE
from multi_agent_system.orchestrator.schemas import PlannerServiceResponse


class FakeSessions:
    def __init__(self) -> None:
        self.created_session_ids: set[str] = set()
        self.create_calls: list[dict] = []
        self.store_calls: list[tuple[str, dict]] = []
        self.flush_calls: list[str] = []
        self.flush_error: Exception | None = None
        self.update_configs_calls: list[dict] = []

    async def create(self, **kwargs):
        self.create_calls.append(kwargs)
        session_id = kwargs["use_uuid"]
        if session_id in self.created_session_ids:
            raise APIError(status_code=409, message="already exists")
        self.created_session_ids.add(session_id)

    async def store_message(self, session_id, **kwargs):
        self.store_calls.append((session_id, kwargs))

    async def flush(self, session_id):
        self.flush_calls.append(session_id)
        if self.flush_error is not None:
            raise self.flush_error

    async def update_configs(self, session_id, *, configs):
        self.update_configs_calls.append(
            {"session_id": session_id, "configs": configs}
        )


class FakeLearningSpaces:
    def __init__(
        self,
        *,
        existing_space: bool = False,
        list_error: Exception | None = None,
    ) -> None:
        self.space_id = "existing-space" if existing_space else None
        self.list_error = list_error
        self.associated_session_ids: set[str] = set()
        self.list_calls: list[dict] = []
        self.create_calls: list[dict] = []
        self.get_session_calls: list[tuple[str, str]] = []
        self.learn_calls: list[tuple[str, str]] = []

    async def list(self, **kwargs):
        self.list_calls.append(kwargs)
        if self.list_error is not None:
            raise self.list_error
        items = [SimpleNamespace(id=self.space_id)] if self.space_id else []
        return SimpleNamespace(items=items)

    async def create(self, **kwargs):
        self.create_calls.append(kwargs)
        self.space_id = "created-space"
        return SimpleNamespace(id=self.space_id)

    async def get_session(self, space_id, *, session_id):
        self.get_session_calls.append((space_id, session_id))
        if session_id not in self.associated_session_ids:
            raise APIError(status_code=404, message="not found")
        return SimpleNamespace(session_id=session_id)

    async def learn(self, space_id, *, session_id):
        self.learn_calls.append((space_id, session_id))
        self.associated_session_ids.add(session_id)


class FakeClient:
    def __init__(
        self,
        *,
        existing_space: bool = False,
        list_error: Exception | None = None,
    ) -> None:
        self.sessions = FakeSessions()
        self.learning_spaces = FakeLearningSpaces(
            existing_space=existing_space,
            list_error=list_error,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _capture(client: FakeClient) -> AcontextCapture:
    return AcontextCapture(
        api_key="test-key",
        base_url="https://example.test/api/v1",
        user_identifier="planner-service",
        client_factory=lambda: client,
    )


@pytest.mark.anyio
async def test_completed_interaction_is_stored_for_skill_learning() -> None:
    client = FakeClient()
    capture = _capture(client)
    response = PlannerServiceResponse(
        status="completed",
        thread_id="thread-1",
        final_answer="Done.",
    )

    await capture.capture(
        user_input="hello",
        thread_id="thread-1",
        resume=False,
        response=response,
    )

    session_id = acontext_session_id("thread-1")
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
    assert client.learning_spaces.create_calls == [
        {
            "user": "planner-service",
            "meta": {
                "source": "multi_agent_system.planner",
                "memory_scope": MEMORY_SCOPE,
            },
        }
    ]
    assert client.sessions.create_calls == [
        {
            "user": "planner-service",
            "disable_task_tracking": True,
            "configs": {
                "source": "multi_agent_system.planner",
                "memory_scope": MEMORY_SCOPE,
                "capture_policy": MEMORY_SCOPE,
                "task_tracking": "disabled",
            },
            "use_uuid": session_id,
        }
    ]
    assert client.sessions.store_calls == [
        (
            session_id,
            {
                "blob": {"role": "user", "content": "hello"},
                "format": "openai",
                "meta": {
                    "message_kind": "skill_learning_user_input",
                    "resume": False,
                    "capture_policy": MEMORY_SCOPE,
                },
            },
        ),
        (
            session_id,
            {
                "blob": {"role": "assistant", "content": "Done."},
                "format": "openai",
                "meta": {
                    "message_kind": "skill_learning_final_response",
                    "planner_status": "completed",
                    "capture_policy": MEMORY_SCOPE,
                },
            },
        ),
    ]
    assert client.sessions.flush_calls == [session_id]
    assert client.learning_spaces.learn_calls == [("created-space", session_id)]


@pytest.mark.anyio
async def test_existing_learning_space_is_reused() -> None:
    client = FakeClient(existing_space=True)
    capture = _capture(client)
    response = PlannerServiceResponse(
        status="completed",
        thread_id="thread-existing",
        final_answer="Done.",
    )

    await capture.capture(
        user_input="hello",
        thread_id="thread-existing",
        resume=False,
        response=response,
    )

    assert client.learning_spaces.create_calls == []
    assert client.learning_spaces.learn_calls == [
        ("existing-space", acontext_session_id("thread-existing"))
    ]


@pytest.mark.anyio
async def test_existing_session_updates_configs_with_task_tracking_disabled() -> None:
    client = FakeClient()
    session_id = acontext_session_id("existing-session")
    client.sessions.created_session_ids.add(session_id)
    capture = _capture(client)
    response = PlannerServiceResponse(
        status="completed",
        thread_id="existing-session",
        final_answer="Done.",
    )

    await capture.capture(
        user_input="hello",
        thread_id="existing-session",
        resume=False,
        response=response,
    )

    assert client.sessions.update_configs_calls == [
        {
            "session_id": session_id,
            "configs": {
                "source": "multi_agent_system.planner",
                "memory_scope": MEMORY_SCOPE,
                "capture_policy": MEMORY_SCOPE,
                "task_tracking": "disabled",
            },
        }
    ]


@pytest.mark.anyio
async def test_failed_interaction_is_stored_but_not_learned() -> None:
    client = FakeClient()
    capture = _capture(client)
    response = PlannerServiceResponse(
        status="failed",
        thread_id="thread-failed",
        final_answer="System error: graph exploded",
    )

    await capture.capture(
        user_input="latest invoice",
        thread_id="thread-failed",
        resume=False,
        response=response,
    )

    assert client.sessions.store_calls[1][1]["meta"]["planner_status"] == "failed"
    assert client.sessions.flush_calls == []
    assert client.learning_spaces.learn_calls == []


@pytest.mark.anyio
async def test_capture_skips_acontext_transport_errors(caplog) -> None:
    client = FakeClient(list_error=TransportError("All connection attempts failed"))
    capture = _capture(client)
    response = PlannerServiceResponse(
        status="completed",
        thread_id="thread-offline",
        final_answer="Done.",
    )

    with caplog.at_level("WARNING"):
        await capture.capture(
            user_input="hello",
            thread_id="thread-offline",
            resume=False,
            response=response,
        )

    assert "Acontext skill learning skipped for planner thread thread-offline" in caplog.text
    assert client.sessions.store_calls == []


@pytest.mark.anyio
async def test_flush_failure_is_non_fatal_and_does_not_check_tasks(caplog) -> None:
    client = FakeClient()
    client.sessions.flush_error = APIError(
        status_code=500,
        message="failed to flush session",
    )
    capture = _capture(client)
    response = PlannerServiceResponse(
        status="completed",
        thread_id="flush-failure-thread",
        final_answer="Done.",
    )

    with caplog.at_level("WARNING"):
        await capture.capture(
            user_input="recommend Jazz songs",
            thread_id="flush-failure-thread",
            resume=False,
            response=response,
        )

    assert "failed to flush session" in caplog.text
    assert "task extraction" not in caplog.text
    assert client.learning_spaces.learn_calls == []


def test_session_identifier_is_stable_for_existing_thread_ids() -> None:
    assert acontext_session_id("thread-1") == acontext_session_id("thread-1")
    assert acontext_session_id("thread-1") != acontext_session_id("thread-2")


def test_build_capture_requires_enabled_configuration(monkeypatch) -> None:
    monkeypatch.setattr(settings, "acontext_enabled", False)
    monkeypatch.setattr(settings, "acontext_api_key", "test-key")

    assert build_acontext_capture() is None


def test_build_capture_skips_missing_api_key_when_enabled(monkeypatch) -> None:
    monkeypatch.setattr(settings, "acontext_enabled", True)
    monkeypatch.setattr(settings, "acontext_api_key", None)

    assert build_acontext_capture() is None
