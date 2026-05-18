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


@pytest.mark.anyio
async def test_ask_extracts_text_from_nested_message_parts() -> None:
    client = StubA2AClient(
        {
            "jsonrpc": "2.0",
            "id": "test-id",
            "result": {
                "message": {
                    "parts": [
                        {
                            "text": "hello from nested message",
                        }
                    ]
                }
            },
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
            "result": {
                "parts": [
                    {
                        "text": "hello from direct result",
                    }
                ]
            },
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
            "result": {
                "message": {
                    "parts": [
                        {"text": "first"},
                        {"text": "second"},
                    ]
                }
            },
        }
    )

    result = await client.ask("hello")

    assert result == "first\nsecond"


@pytest.mark.anyio
async def test_ask_raises_when_result_is_missing() -> None:
    client = StubA2AClient(
        {
            "jsonrpc": "2.0",
            "id": "test-id",
        }
    )

    with pytest.raises(A2AClientError, match="missing result"):
        await client.ask("hello")


@pytest.mark.anyio
async def test_ask_raises_when_parts_are_missing() -> None:
    client = StubA2AClient(
        {
            "jsonrpc": "2.0",
            "id": "test-id",
            "result": {
                "message": {},
            },
        }
    )

    with pytest.raises(A2AClientError, match="missing message parts"):
        await client.ask("hello")


@pytest.mark.anyio
async def test_ask_raises_when_part_text_is_missing() -> None:
    client = StubA2AClient(
        {
            "jsonrpc": "2.0",
            "id": "test-id",
            "result": {
                "message": {
                    "parts": [
                        {
                            "type": "text",
                        }
                    ]
                }
            },
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
            "result": {
                "message": {
                    "parts": [
                        {
                            "text": "   ",
                        }
                    ]
                }
            },
        }
    )

    with pytest.raises(A2AClientError, match="empty text response"):
        await client.ask("hello")
