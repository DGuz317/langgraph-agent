import json
from types import SimpleNamespace

import pytest

from acontext.errors import APIError, TransportError

from multi_agent_system.common.execution_evidence import ExecutionEvidence
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
        self.get_tasks_calls: list[dict] = []
        self.update_configs_calls: list[dict] = []
        self.disable_task_tracking = False
        self.tasks: list[object] = []

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

    async def get_tasks(self, session_id, **kwargs):
        self.get_tasks_calls.append({"session_id": session_id, **kwargs})
        return SimpleNamespace(items=self.tasks)

    async def update_configs(self, session_id, *, configs):
        self.update_configs_calls.append(
            {"session_id": session_id, "configs": configs}
        )

    async def get_configs(self, session_id):
        return SimpleNamespace(disable_task_tracking=self.disable_task_tracking)


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
    assert client.learning_spaces.learn_calls == [("created-space", session_id)]
    assert client.sessions.create_calls == [
        {
            "user": "planner-service",
            "disable_task_tracking": False,
            "configs": {
                "source": "multi_agent_system.planner",
                "memory_scope": MEMORY_SCOPE,
                "capture_policy": MEMORY_SCOPE,
                "task_tracking": "enabled",
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
                    "content": "hello",
                },
                "format": "openai",
                "meta": {
                    "message_kind": "user_input",
                    "resume": False,
                    "capture_policy": MEMORY_SCOPE,
                },
            },
        ),
        (
            session_id,
            {
                "blob": {
                    "role": "assistant",
                    "content": "Done.",
                },
                "format": "openai",
                "meta": {
                    "message_kind": "final_response",
                    "planner_status": "completed",
                    "capture_policy": MEMORY_SCOPE,
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
    assert len(client.sessions.store_calls) == 4
    assert client.sessions.store_calls[1][1]["blob"]["content"] == "Provide customer ID."
    assert client.sessions.store_calls[3][1]["blob"]["content"] == "Latest invoice found."
    assert client.sessions.flush_calls == [session_id]
    assert client.sessions.update_configs_calls == [
        {
            "session_id": session_id,
            "configs": {
                "source": "multi_agent_system.planner",
                "memory_scope": MEMORY_SCOPE,
                "capture_policy": MEMORY_SCOPE,
                "task_tracking": "enabled",
            },
        }
    ]


@pytest.mark.anyio
async def test_existing_session_warns_when_task_tracking_is_disabled(caplog) -> None:
    client = FakeClient()
    client.sessions.disable_task_tracking = True
    session_id = acontext_session_id("existing-disabled-session")
    client.sessions.created_session_ids.add(session_id)
    capture = _capture(client)
    response = PlannerServiceResponse(
        status="completed",
        thread_id="existing-disabled-session",
        final_answer="Done.",
    )

    with caplog.at_level("WARNING"):
        await capture.capture(
            user_input="hello",
            thread_id="existing-disabled-session",
            resume=False,
            response=response,
        )

    assert "disable_task_tracking=true" in caplog.text


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

    assert "Acontext capture skipped for planner thread thread-offline" in caplog.text
    assert client.sessions.store_calls == []


@pytest.mark.anyio
async def test_workflow_outcome_capture_stores_readable_trace_and_final_answer() -> None:
    client = FakeClient()
    client.sessions.tasks = [SimpleNamespace(id="task-1")]
    capture = _capture(client)
    call_id = "tool-call-1"
    response = PlannerServiceResponse(
        status="completed",
        thread_id="sensitive-thread",
        final_answer="customer_id=5 BillingAddress=Example email=support@example.com",
        raw_result={
            "planner_output": {
                "tasks": [
                    {
                        "agent": "invoice",
                        "status": "completed",
                        "instruction": "Get latest invoice for customer_id=5",
                    }
                ],
            },
            "execution_evidence": [
                ExecutionEvidence(
                    kind="planner_decision",
                    agent="planner",
                    operation="invoice",
                    status="completed",
                    summary="Planner selected an executable agent dispatch.",
                ).model_dump(),
                ExecutionEvidence(
                    kind="mcp_tool_call",
                    agent="invoice",
                    operation="get_invoices_by_customer_sorted_by_date",
                    status="started",
                    call_id=call_id,
                    fields=["customer_id"],
                    arguments={"customer_id": "5"},
                    summary="Called invoice lookup.",
                ).model_dump(),
                ExecutionEvidence(
                    kind="mcp_tool_result",
                    agent="invoice",
                    operation="get_invoices_by_customer_sorted_by_date",
                    status="completed",
                    call_id=call_id,
                    summary=(
                        "Invoice lookup completed. Outcome: "
                        '{"InvoiceId": 1, "CustomerId": 5}'
                    ),
                ).model_dump(),
                ExecutionEvidence(
                    kind="agent_result",
                    agent="invoice",
                    operation="agent_instruction",
                    status="completed",
                    summary="Domain agent completed the instruction.",
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

    assert blobs[0] == {
        "role": "user",
        "content": "Get latest invoice for customer_id=5",
    }
    assert "Acontext task extraction summary" in captured_json
    assert "Task 1: invoice agent should complete the instruction" in captured_json
    assert "Get latest invoice for customer_id=5" in captured_json
    assert "completed tool get_invoices_by_customer_sorted_by_date" in captured_json
    assert "Invoice agent called MCP tool" not in captured_json
    assert "Invoice lookup completed. Outcome:" in captured_json
    tool_result_blob = next(blob for blob in blobs if blob.get("role") == "tool")
    assert '"InvoiceId": 1' in tool_result_blob["content"]
    assert "Invoice agent completed latest_invoice." not in captured_json
    assert "customer_id=5 BillingAddress=Example email=support@example.com" in captured_json
    tool_call_blob = next(blob for blob in blobs if blob.get("tool_calls"))
    assert tool_call_blob["content"] == ""
    assert json.loads(
        tool_call_blob["tool_calls"][0]["function"]["arguments"]
    ) == {"customer_id": "5"}
    assert client.sessions.get_tasks_calls == [
        {"session_id": acontext_session_id("sensitive-thread"), "limit": 1}
    ]


@pytest.mark.anyio
async def test_capture_warns_when_acontext_extracts_no_tasks(caplog) -> None:
    client = FakeClient()
    capture = _capture(client)
    response = PlannerServiceResponse(
        status="completed",
        thread_id="no-acontext-tasks",
        final_answer="Done.",
        raw_result={
            "planner_output": {
                "tasks": [
                    {
                        "agent": "music",
                        "instruction": "Recommend Jazz songs.",
                        "status": "completed",
                    }
                ]
            }
        },
    )

    with caplog.at_level("WARNING"):
        await capture.capture(
            user_input="recommend Jazz songs",
            thread_id="no-acontext-tasks",
            resume=False,
            response=response,
        )

    assert "Acontext extracted no tasks for planner thread no-acontext-tasks" in caplog.text


@pytest.mark.anyio
async def test_resume_does_not_store_repeated_trace_messages() -> None:
    client = FakeClient()
    capture = _capture(client)
    tool_call = ExecutionEvidence(
        kind="mcp_tool_call",
        agent="invoice",
        operation="get_invoices_by_customer_sorted_by_date",
        status="started",
        call_id="tool-call-1",
        fields=["customer_id"],
        summary="Invoked invoice lookup.",
    ).model_dump()

    await capture.capture(
        user_input="Get latest invoice",
        thread_id="resume-evidence",
        resume=False,
        response=PlannerServiceResponse(
            status="interrupted",
            thread_id="resume-evidence",
            interrupt_message="Provide a customer identifier.",
            raw_result={"execution_evidence": [tool_call]},
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
            raw_result={"execution_evidence": [tool_call]},
        ),
    )

    trace_messages = [
        kwargs
        for _, kwargs in client.sessions.store_calls
        if kwargs["meta"].get("trace_kind") == "mcp_tool_call"
    ]
    assert len(trace_messages) == 1


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
