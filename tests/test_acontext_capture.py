import json
from types import SimpleNamespace

import pytest

from acontext.errors import APIError

from multi_agent_system.common.execution_evidence import ExecutionEvidence
from multi_agent_system.config import settings
from multi_agent_system.orchestrator.acontext_capture import (
    AcontextCapture,
    acontext_session_id,
    build_acontext_capture,
)
from multi_agent_system.orchestrator.schemas import PlannerServiceResponse


class FakeSessions:
    def __init__(self) -> None:
        self.created_session_ids: set[str] = set()
        self.create_calls: list[dict] = []
        self.store_calls: list[tuple[str, dict]] = []
        self.flush_calls: list[str] = []

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


class FakeLearningSpaces:
    def __init__(self, *, existing_space: bool = False) -> None:
        self.space_id = "existing-space" if existing_space else None
        self.associated_session_ids: set[str] = set()
        self.list_calls: list[dict] = []
        self.create_calls: list[dict] = []
        self.get_session_calls: list[tuple[str, str]] = []
        self.learn_calls: list[tuple[str, str]] = []

    async def list(self, **kwargs):
        self.list_calls.append(kwargs)
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
    def __init__(self, *, existing_space: bool = False) -> None:
        self.sessions = FakeSessions()
        self.learning_spaces = FakeLearningSpaces(existing_space=existing_space)

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
async def test_completed_interaction_creates_learning_space_and_flushes() -> None:
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
                "memory_scope": "sanitized-execution-v1",
            },
        }
    ]
    assert client.learning_spaces.create_calls == [
        {
            "user": "planner-service",
            "meta": {
                "source": "multi_agent_system.planner",
                "memory_scope": "sanitized-execution-v1",
            },
        }
    ]
    assert client.learning_spaces.learn_calls == [("created-space", session_id)]
    assert client.sessions.create_calls == [
        {
            "user": "planner-service",
            "configs": {
                "source": "multi_agent_system.planner",
                "memory_scope": "sanitized-execution-v1",
                "capture_policy": "sanitized-execution-v1",
            },
            "use_uuid": session_id,
        }
    ]
    assert client.sessions.store_calls == [
        (
            session_id,
            {
                "blob": {
                    "role": "user",
                    "content": "Submitted a planner request. User content omitted from memory.",
                },
                "format": "openai",
                "meta": {
                    "resume": False,
                    "capture_policy": "sanitized-execution-v1",
                },
            },
        ),
        (
            session_id,
            {
                "blob": {
                    "role": "assistant",
                    "content": "Planner workflow completed. Returned content omitted from memory.",
                },
                "format": "openai",
                "meta": {
                    "planner_status": "completed",
                    "capture_policy": "sanitized-execution-v1",
                },
            },
        ),
    ]
    assert client.sessions.flush_calls == [session_id]


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
async def test_interrupt_and_resume_share_learning_session_and_flush_at_end() -> None:
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
    assert client.learning_spaces.learn_calls == [("created-space", session_id)]
    assert len(client.sessions.store_calls) == 5
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


@pytest.mark.anyio
async def test_execution_evidence_is_stored_without_raw_business_values() -> None:
    client = FakeClient()
    capture = _capture(client)
    call_id = "tool-call-1"
    response = PlannerServiceResponse(
        status="completed",
        thread_id="sensitive-thread",
        final_answer="customer_id=5 BillingAddress=Example email=support@example.com",
        raw_result={
            "execution_evidence": [
                ExecutionEvidence(
                    kind="planner_decision",
                    agent="planner",
                    operation="latest_invoice",
                    status="completed",
                    fields=["customer_id"],
                    summary="Planner selected an executable workflow; values omitted from memory.",
                ).model_dump(),
                ExecutionEvidence(
                    kind="mcp_tool_call",
                    agent="invoice",
                    operation="get_invoices_by_customer_sorted_by_date",
                    status="started",
                    call_id=call_id,
                    fields=["customer_id"],
                    summary="Invoked invoice lookup; supplied values omitted from memory.",
                ).model_dump(),
                ExecutionEvidence(
                    kind="mcp_tool_result",
                    agent="invoice",
                    operation="get_invoices_by_customer_sorted_by_date",
                    status="completed",
                    call_id=call_id,
                    summary="Invoice lookup completed; returned values omitted from memory.",
                ).model_dump(),
                ExecutionEvidence(
                    kind="agent_result",
                    agent="invoice",
                    operation="latest_invoice",
                    status="completed",
                    summary="Domain workflow completed; returned values omitted from memory.",
                ).model_dump(),
            ]
        },
    )

    await capture.capture(
        user_input="Get latest invoice for customer_id=5",
        thread_id="sensitive-thread",
        resume=False,
        response=response,
    )

    blobs = [kwargs["blob"] for _, kwargs in client.sessions.store_calls]
    captured_json = json.dumps(blobs)

    assert "customer_id=5" not in captured_json
    assert "BillingAddress" not in captured_json
    assert "support@example.com" not in captured_json
    assert blobs[0]["content"].startswith("Requested workflow: latest_invoice")
    assert any(blob.get("tool_calls") for blob in blobs)
    assert any(blob.get("role") == "tool" for blob in blobs)


@pytest.mark.anyio
async def test_resume_does_not_store_repeated_execution_evidence() -> None:
    client = FakeClient()
    capture = _capture(client)
    decision = ExecutionEvidence(
        kind="planner_decision",
        agent="planner",
        operation="latest_invoice",
        status="interrupted",
        fields=["customer_id"],
        summary="Planner selected a workflow requiring additional fields.",
    ).model_dump()

    await capture.capture(
        user_input="Get latest invoice",
        thread_id="resume-evidence",
        resume=False,
        response=PlannerServiceResponse(
            status="interrupted",
            thread_id="resume-evidence",
            interrupt_message="Provide a customer identifier.",
            raw_result={"execution_evidence": [decision]},
        ),
    )
    await capture.capture(
        user_input="5",
        thread_id="resume-evidence",
        resume=True,
        response=PlannerServiceResponse(
            status="completed",
            thread_id="resume-evidence",
            final_answer="Sensitive response",
            raw_result={"execution_evidence": [decision]},
        ),
    )

    evidence_messages = [
        kwargs
        for _, kwargs in client.sessions.store_calls
        if kwargs["meta"].get("evidence_kind") == "planner_decision"
    ]
    assert len(evidence_messages) == 1


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
