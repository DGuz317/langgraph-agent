import json

import httpx
import pytest

from multi_agent_system.a2a_client.base import BaseA2AClient
from multi_agent_system.common.errors import A2AClientError


class StubA2AClient(BaseA2AClient):
    def __init__(self, body: dict) -> None:
        super().__init__(
            url="http://testserver/a2a/jsonrpc/",
            timeout_seconds=1,
        )
        self.body = body
        self.last_text: str | None = None

    async def send_message(self, text: str) -> dict:
        self.last_text = text
        return self.body


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def make_client(transport: httpx.AsyncBaseTransport) -> BaseA2AClient:
    return BaseA2AClient(
        url="http://testserver/a2a/jsonrpc/",
        timeout_seconds=1,
        transport=transport,
    )


@pytest.mark.anyio
async def test_send_message_returns_jsonrpc_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": "test-id",
                "result": {"message": {"parts": [{"text": "ok"}]}},
            },
        )

    body = await make_client(httpx.MockTransport(handler)).send_message("hello")

    assert body["jsonrpc"] == "2.0"
    assert "result" in body


@pytest.mark.anyio
async def test_ask_payload_sends_data_and_compatibility_text_parts() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": "test-id",
                "result": {"message": {"parts": [{"text": "ok"}]}},
            },
        )

    payload = {
        "agent": "invoice",
        "intent": "latest_invoice",
        "args": {"customer_id": "5"},
        "instruction": "Get latest invoice for customer_id=5",
    }

    result = await make_client(httpx.MockTransport(handler)).ask_payload(payload)

    assert result == "ok"
    assert captured["params"]["message"]["parts"] == [
        {"data": payload},
        {"text": payload["instruction"]},
    ]


@pytest.mark.anyio
async def test_send_message_raises_on_http_500() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="server exploded")

    with pytest.raises(A2AClientError, match="HTTP 500"):
        await make_client(httpx.MockTransport(handler)).send_message("hello")


@pytest.mark.anyio
async def test_send_message_raises_on_invalid_json() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not json")

    with pytest.raises(A2AClientError, match="not valid JSON"):
        await make_client(httpx.MockTransport(handler)).send_message("hello")


@pytest.mark.anyio
async def test_send_message_raises_on_jsonrpc_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": "test-id",
                "error": {"code": -32601, "message": "Method not found"},
            },
        )

    with pytest.raises(A2AClientError, match="JSON-RPC error"):
        await make_client(httpx.MockTransport(handler)).send_message("hello")


@pytest.mark.anyio
async def test_send_message_raises_on_connection_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    with pytest.raises(A2AClientError, match="request failed"):
        await make_client(httpx.MockTransport(handler)).send_message("hello")


@pytest.mark.anyio
async def test_send_message_raises_on_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    with pytest.raises(A2AClientError, match="timed out"):
        await make_client(httpx.MockTransport(handler)).send_message("hello")


@pytest.mark.anyio
async def test_ask_extracts_text_from_nested_message_parts() -> None:
    client = StubA2AClient(
        {
            "jsonrpc": "2.0",
            "id": "test-id",
            "result": {"message": {"parts": [{"text": "hello from nested message"}]}},
        }
    )

    result = await client.ask("hello")

    assert client.last_text == "hello"
    assert result == "hello from nested message"


@pytest.mark.anyio
async def test_ask_extracts_text_from_direct_result_parts() -> None:
    client = StubA2AClient(
        {
            "jsonrpc": "2.0",
            "id": "test-id",
            "result": {"parts": [{"text": "hello from direct result"}]},
        }
    )

    result = await client.ask("hello")

    assert result == "hello from direct result"


@pytest.mark.anyio
async def test_ask_combines_multiple_text_parts() -> None:
    client = StubA2AClient(
        {
            "jsonrpc": "2.0",
            "id": "test-id",
            "result": {"message": {"parts": [{"text": "first"}, {"text": "second"}]}},
        }
    )

    result = await client.ask("hello")

    assert result == "first\nsecond"


@pytest.mark.anyio
async def test_ask_raises_when_result_is_missing() -> None:
    client = StubA2AClient({"jsonrpc": "2.0", "id": "test-id"})

    with pytest.raises(A2AClientError, match="missing result"):
        await client.ask("hello")


@pytest.mark.anyio
async def test_ask_raises_when_parts_are_missing() -> None:
    client = StubA2AClient(
        {"jsonrpc": "2.0", "id": "test-id", "result": {"message": {}}}
    )

    with pytest.raises(A2AClientError, match="missing message parts"):
        await client.ask("hello")


@pytest.mark.anyio
async def test_ask_raises_when_part_text_is_missing() -> None:
    client = StubA2AClient(
        {
            "jsonrpc": "2.0",
            "id": "test-id",
            "result": {"message": {"parts": [{"type": "text"}]}},
        }
    )

    with pytest.raises(A2AClientError, match="missing text content"):
        await client.ask("hello")


@pytest.mark.anyio
async def test_ask_raises_when_text_is_empty() -> None:
    client = StubA2AClient(
        {
            "jsonrpc": "2.0",
            "id": "test-id",
            "result": {"message": {"parts": [{"text": "   "}]}},
        }
    )

    with pytest.raises(A2AClientError, match="empty text response"):
        await client.ask("hello")


@pytest.mark.anyio
async def test_invoice_client_get_latest_invoice_builds_expected_instruction(
    monkeypatch,
) -> None:
    from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient

    captured: dict[str, str] = {}

    async def fake_ask(self, instruction: str) -> str:
        captured["instruction"] = instruction
        return "invoice-ok"

    monkeypatch.setattr(InvoiceA2AClient, "ask", fake_ask)

    client = object.__new__(InvoiceA2AClient)
    result = await client.get_latest_invoice("5")

    assert result == "invoice-ok"
    assert captured["instruction"] == "Get latest invoice for customer_id=5"


@pytest.mark.anyio
async def test_invoice_client_get_invoice_detail_builds_expected_instruction(
    monkeypatch,
) -> None:
    from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient

    captured: dict[str, str] = {}

    async def fake_ask(self, instruction: str) -> str:
        captured["instruction"] = instruction
        return "invoice-ok"

    monkeypatch.setattr(InvoiceA2AClient, "ask", fake_ask)

    client = object.__new__(InvoiceA2AClient)
    result = await client.get_invoice_detail("361")

    assert result == "invoice-ok"
    assert captured["instruction"] == "Get invoice detail for invoice_id=361"


@pytest.mark.anyio
async def test_invoice_client_get_invoice_summary_builds_expected_instruction(
    monkeypatch,
) -> None:
    from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient

    captured: dict[str, str] = {}

    async def fake_ask(self, instruction: str) -> str:
        captured["instruction"] = instruction
        return "invoice-ok"

    monkeypatch.setattr(InvoiceA2AClient, "ask", fake_ask)

    client = object.__new__(InvoiceA2AClient)
    result = await client.get_invoice_summary("5")

    assert result == "invoice-ok"
    assert captured["instruction"] == "Get invoice summary for customer_id=5"


@pytest.mark.anyio
async def test_invoice_client_get_customer_support_employee_builds_expected_instruction(
    monkeypatch,
) -> None:
    from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient

    captured: dict[str, str] = {}

    async def fake_ask(self, instruction: str) -> str:
        captured["instruction"] = instruction
        return "invoice-ok"

    monkeypatch.setattr(InvoiceA2AClient, "ask", fake_ask)

    client = object.__new__(InvoiceA2AClient)
    result = await client.get_customer_support_employee("5")

    assert result == "invoice-ok"
    assert captured["instruction"] == "Get support employee for customer_id=5"


@pytest.mark.anyio
async def test_music_client_get_tracks_by_artist_builds_expected_instruction(
    monkeypatch,
) -> None:
    from multi_agent_system.a2a_client.music_client import MusicA2AClient

    captured: dict[str, str] = {}

    async def fake_ask(self, instruction: str) -> str:
        captured["instruction"] = instruction
        return "music-ok"

    monkeypatch.setattr(MusicA2AClient, "ask", fake_ask)

    client = object.__new__(MusicA2AClient)
    result = await client.get_tracks_by_artist("AC/DC")

    assert result == "music-ok"
    assert captured["instruction"] == "Find tracks by artist AC/DC"
