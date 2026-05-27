import json

import httpx
import pytest
from a2a.helpers import get_message_text, new_data_message, new_text_message
from a2a.types import Role

from multi_agent_system.a2a_servers.invoice_agent.executor import (
    InvoiceAgentExecutor,
)
from multi_agent_system.a2a_servers.invoice_agent.agent import InvoiceAgent
from multi_agent_system.a2a_servers.invoice_agent.schemas import InvoiceAgentResponse
from multi_agent_system.a2a_servers.music_agent.executor import MusicAgentExecutor
from multi_agent_system.a2a_servers.music_agent.schemas import MusicAgentResponse
from multi_agent_system.a2a_client.base import BaseA2AClient
from multi_agent_system.common.execution_evidence import (
    ExecutionEvidence,
    record_execution_evidence,
)


class FakeContext:
    def __init__(self, message) -> None:
        self.message = message

    def get_user_input(self) -> str:
        return get_message_text(self.message)


class FakeEventQueue:
    def __init__(self) -> None:
        self.events = []

    async def enqueue_event(self, event) -> None:
        self.events.append(event)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_invoice_executor_prefers_structured_request_data() -> None:
    captured = {}

    class FakeInvoiceAgent:
        async def invoke_request(self, request):
            captured["request"] = request
            return InvoiceAgentResponse(success=True, content="structured invoice")

        async def ainvoke(self, query: str):
            raise AssertionError("text fallback must not be used")

    executor = InvoiceAgentExecutor()
    executor.agent = FakeInvoiceAgent()
    queue = FakeEventQueue()
    context = FakeContext(
        new_data_message(
            {
                "agent": "invoice",
                "intent": "all_invoices",
                "args": {"customer_id": "5"},
            },
            role=Role.ROLE_USER,
        )
    )

    await executor.execute(context, queue)

    assert captured["request"].intent == "all_invoices"
    assert captured["request"].customer_id == "5"
    assert json.loads(get_message_text(queue.events[0]))["content"] == "structured invoice"


@pytest.mark.anyio
async def test_invoice_executor_returns_collected_sanitized_evidence() -> None:
    class FakeInvoiceAgent:
        async def invoke_request(self, request):
            record_execution_evidence(
                ExecutionEvidence(
                    kind="mcp_tool_result",
                    agent="invoice",
                    operation="get_invoice_summary_by_customer",
                    status="completed",
                    summary="Tool completed; returned values omitted from memory.",
                )
            )
            return InvoiceAgentResponse(success=True, content="structured invoice")

    executor = InvoiceAgentExecutor()
    executor.agent = FakeInvoiceAgent()
    queue = FakeEventQueue()
    await executor.execute(
        FakeContext(
            new_data_message(
                {
                    "agent": "invoice",
                    "intent": "invoice_summary",
                    "args": {"customer_id": "5"},
                },
                role=Role.ROLE_USER,
            )
        ),
        queue,
    )

    result = json.loads(get_message_text(queue.events[0]))
    assert result["execution_evidence"][0]["operation"] == "get_invoice_summary_by_customer"
    assert "customer_id=5" not in result["execution_evidence"][0]["summary"]


@pytest.mark.anyio
async def test_invoice_executor_dispatches_structured_invoice_detail() -> None:
    captured = {}

    class FakeInvoiceAgent:
        async def invoke_request(self, request):
            captured["request"] = request
            return InvoiceAgentResponse(success=True, content="invoice detail")

        async def ainvoke(self, query: str):
            raise AssertionError("text fallback must not be used")

    executor = InvoiceAgentExecutor()
    executor.agent = FakeInvoiceAgent()
    queue = FakeEventQueue()

    await executor.execute(
        FakeContext(
            new_data_message(
                {
                    "agent": "invoice",
                    "intent": "invoice_detail",
                    "args": {"invoice_id": "361"},
                },
                role=Role.ROLE_USER,
            )
        ),
        queue,
    )

    assert captured["request"].intent == "invoice_detail"
    assert captured["request"].invoice_id == "361"


@pytest.mark.anyio
async def test_invoice_executor_dispatches_structured_invoice_summary() -> None:
    captured = {}

    class FakeInvoiceAgent:
        async def invoke_request(self, request):
            captured["request"] = request
            return InvoiceAgentResponse(success=True, content="invoice summary")

        async def ainvoke(self, query: str):
            raise AssertionError("text fallback must not be used")

    executor = InvoiceAgentExecutor()
    executor.agent = FakeInvoiceAgent()
    queue = FakeEventQueue()

    await executor.execute(
        FakeContext(
            new_data_message(
                {
                    "agent": "invoice",
                    "intent": "invoice_summary",
                    "args": {"customer_id": "5"},
                },
                role=Role.ROLE_USER,
            )
        ),
        queue,
    )

    assert captured["request"].intent == "invoice_summary"
    assert captured["request"].customer_id == "5"


@pytest.mark.anyio
async def test_invoice_executor_dispatches_structured_customer_support_employee() -> None:
    captured = {}

    class FakeInvoiceAgent:
        async def invoke_request(self, request):
            captured["request"] = request
            return InvoiceAgentResponse(success=True, content="support employee")

        async def ainvoke(self, query: str):
            raise AssertionError("text fallback must not be used")

    executor = InvoiceAgentExecutor()
    executor.agent = FakeInvoiceAgent()
    queue = FakeEventQueue()

    await executor.execute(
        FakeContext(
            new_data_message(
                {
                    "agent": "invoice",
                    "intent": "customer_support_employee",
                    "args": {"customer_id": "5"},
                },
                role=Role.ROLE_USER,
            )
        ),
        queue,
    )

    assert captured["request"].intent == "customer_support_employee"
    assert captured["request"].customer_id == "5"


@pytest.mark.anyio
async def test_invoice_executor_falls_back_to_text_without_data_part() -> None:
    captured = {}

    class FakeInvoiceAgent:
        async def invoke_request(self, request):
            raise AssertionError("structured dispatch must not be used")

        async def ainvoke(self, query: str):
            captured["query"] = query
            return InvoiceAgentResponse(success=True, content="legacy text")

    executor = InvoiceAgentExecutor()
    executor.agent = FakeInvoiceAgent()
    queue = FakeEventQueue()

    await executor.execute(
        FakeContext(
            new_text_message(
                "Get latest invoice for customer_id=5",
                role=Role.ROLE_USER,
            )
        ),
        queue,
    )

    assert captured["query"] == "Get latest invoice for customer_id=5"
    assert json.loads(get_message_text(queue.events[0]))["content"] == "legacy text"


@pytest.mark.anyio
async def test_invoice_executor_rejects_invalid_structured_data_without_text_fallback() -> None:
    class FakeInvoiceAgent:
        async def invoke_request(self, request):
            raise AssertionError("invalid structured data must not execute")

        async def ainvoke(self, query: str):
            raise AssertionError("invalid structured data must not fall back")

    executor = InvoiceAgentExecutor()
    executor.agent = FakeInvoiceAgent()
    queue = FakeEventQueue()

    await executor.execute(
        FakeContext(
            new_data_message(
                {
                    "agent": "music",
                    "intent": "tracks_by_artist",
                    "args": {"artist": "AC/DC"},
                },
                role=Role.ROLE_USER,
            )
        ),
        queue,
    )

    result = json.loads(get_message_text(queue.events[0]))
    assert result["success"] is False
    assert result["content"] == "Invalid structured invoice request."


@pytest.mark.anyio
async def test_music_executor_dispatches_structured_request_data() -> None:
    captured = {}

    class FakeMusicAgent:
        async def invoke_request(self, request):
            captured["request"] = request
            return MusicAgentResponse(success=True, content="structured music")

        async def ainvoke(self, query: str):
            raise AssertionError("text fallback must not be used")

    executor = MusicAgentExecutor()
    executor.agent = FakeMusicAgent()
    queue = FakeEventQueue()

    await executor.execute(
        FakeContext(
            new_data_message(
                {
                    "agent": "music",
                    "intent": "tracks_by_artist",
                    "args": {"artist": "AC/DC"},
                },
                role=Role.ROLE_USER,
            )
        ),
        queue,
    )

    assert captured["request"].intent == "tracks_by_artist"
    assert captured["request"].artist == "AC/DC"
    assert json.loads(get_message_text(queue.events[0]))["content"] == "structured music"


@pytest.mark.anyio
async def test_jsonrpc_route_preserves_structured_a2a_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from multi_agent_system.a2a_servers.invoice_agent.server import create_app

    captured = {}

    async def fake_invoke_request(self, request):
        captured["request"] = request
        return InvoiceAgentResponse(success=True, content="structured over jsonrpc")

    monkeypatch.setattr(InvoiceAgent, "invoke_request", fake_invoke_request)

    client = BaseA2AClient(
        url="http://testserver/a2a/jsonrpc/",
        transport=httpx.ASGITransport(app=create_app()),
    )

    result = await client.ask_payload(
        {
            "agent": "invoice",
            "intent": "latest_invoice",
            "args": {"customer_id": "5"},
            "instruction": "Get latest invoice for customer_id=5",
        }
    )

    assert result
    assert captured["request"].intent == "latest_invoice"
    assert captured["request"].customer_id == "5"
