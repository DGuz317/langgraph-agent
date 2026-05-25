import json

import httpx
import pytest

from multi_agent_system.a2a_client.base import BaseA2AClient
from multi_agent_system.common.errors import A2AClientError


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
                "result": {
                    "message": {
                        "parts": [
                            {
                                "text": "ok",
                            }
                        ]
                    }
                },
            },
        )

    client = make_client(httpx.MockTransport(handler))

    body = await client.send_message("hello")

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

    client = make_client(httpx.MockTransport(handler))
    payload = {
        "agent": "invoice",
        "intent": "latest_invoice",
        "args": {"customer_id": "5"},
        "instruction": "Get latest invoice for customer_id=5",
    }

    result = await client.ask_payload(payload)

    assert result == "ok"
    assert captured["params"]["message"]["parts"] == [
        {"data": payload},
        {"text": payload["instruction"]},
    ]


@pytest.mark.anyio
async def test_send_message_raises_on_http_500() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="server exploded")

    client = make_client(httpx.MockTransport(handler))

    with pytest.raises(A2AClientError, match="HTTP 500"):
        await client.send_message("hello")


@pytest.mark.anyio
async def test_send_message_raises_on_invalid_json() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not json")

    client = make_client(httpx.MockTransport(handler))

    with pytest.raises(A2AClientError, match="not valid JSON"):
        await client.send_message("hello")


@pytest.mark.anyio
async def test_send_message_raises_on_jsonrpc_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": "test-id",
                "error": {
                    "code": -32601,
                    "message": "Method not found",
                },
            },
        )

    client = make_client(httpx.MockTransport(handler))

    with pytest.raises(A2AClientError, match="JSON-RPC error"):
        await client.send_message("hello")


@pytest.mark.anyio
async def test_send_message_raises_on_connection_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client = make_client(httpx.MockTransport(handler))

    with pytest.raises(A2AClientError, match="request failed"):
        await client.send_message("hello")


@pytest.mark.anyio
async def test_send_message_raises_on_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    client = make_client(httpx.MockTransport(handler))

    with pytest.raises(A2AClientError, match="timed out"):
        await client.send_message("hello")
