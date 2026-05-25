import pytest

from acontext.errors import APIError

from multi_agent_system.config import settings
from multi_agent_system.orchestrator.acontext_capture import (
    AcontextCapture,
    acontext_session_id,
    build_acontext_capture,
)
from multi_agent_system.orchestrator.schemas import PlannerServiceResponse


class FakeSessions:
    def __init__(self) -> None:
        self.created_session_ids = set()
        self.create_calls = []
        self.store_calls = []
        self.flush_calls = []

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


class FakeClient:
    def __init__(self) -> None:
        self.sessions = FakeSessions()

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
async def test_completed_interaction_is_stored_and_flushed() -> None:
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
    assert client.sessions.create_calls == [
        {
            "user": "planner-service",
            "configs": {
                "source": "multi_agent_system.planner",
                "planner_thread_id": "thread-1",
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
                "meta": {"planner_thread_id": "thread-1", "resume": False},
            },
        ),
        (
            session_id,
            {
                "blob": {"role": "assistant", "content": "Done."},
                "format": "openai",
                "meta": {
                    "planner_thread_id": "thread-1",
                    "planner_status": "completed",
                },
            },
        ),
    ]
    assert client.sessions.flush_calls == [session_id]


@pytest.mark.anyio
async def test_interrupt_and_resume_share_session_and_flush_on_terminal_result() -> None:
    client = FakeClient()
    capture = _capture(client)
    interrupt_response = PlannerServiceResponse(
        status="interrupted",
        thread_id="customer-flow",
        interrupt_message="Provide customer ID.",
        needs_resume=True,
    )
    completed_response = PlannerServiceResponse(
        status="completed",
        thread_id="customer-flow",
        final_answer="Latest invoice found.",
    )

    await capture.capture(
        user_input="latest invoice",
        thread_id="customer-flow",
        resume=False,
        response=interrupt_response,
    )
    await capture.capture(
        user_input="5",
        thread_id="customer-flow",
        resume=True,
        response=completed_response,
    )

    session_id = acontext_session_id("customer-flow")
    assert [call["use_uuid"] for call in client.sessions.create_calls] == [
        session_id,
        session_id,
    ]
    assert len(client.sessions.store_calls) == 4
    assert client.sessions.flush_calls == [session_id]


@pytest.mark.anyio
async def test_failed_interaction_is_stored_and_flushed() -> None:
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

    session_id = acontext_session_id("thread-failed")
    assert client.sessions.store_calls[1][1]["meta"]["planner_status"] == "failed"
    assert client.sessions.flush_calls == [session_id]


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
