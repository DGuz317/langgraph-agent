import json

import pytest

from multi_agent_system.a2a_servers.invoice_agent.executor import InvoiceAgentExecutor
from multi_agent_system.a2a_servers.invoice_agent.schemas import InvoiceAgentResponse
from multi_agent_system.a2a_servers.music_agent.executor import MusicAgentExecutor
from multi_agent_system.a2a_servers.music_agent.schemas import MusicAgentResponse


class FakeContext:
    def __init__(self, text: str, data: dict | None = None) -> None:
        self._text = text
        self.data = data
        self.message = type("Message", (), {"parts": []})()

    def get_user_input(self) -> str:
        return self._text


class FakeEventQueue:
    def __init__(self) -> None:
        self.events = []

    async def enqueue_event(self, event) -> None:
        self.events.append(event)


class RecordingInvoiceAgent:
    def __init__(self) -> None:
        self.instructions: list[str] = []

    async def ainvoke(self, instruction: str) -> InvoiceAgentResponse:
        self.instructions.append(instruction)
        return InvoiceAgentResponse(success=True, content="invoice ok")


class RecordingMusicAgent:
    def __init__(self) -> None:
        self.instructions: list[str] = []

    async def ainvoke(self, instruction: str) -> MusicAgentResponse:
        self.instructions.append(instruction)
        return MusicAgentResponse(success=True, content="music ok")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_invoice_executor_passes_text_instruction() -> None:
    executor = InvoiceAgentExecutor()
    agent = RecordingInvoiceAgent()
    executor.agent = agent
    queue = FakeEventQueue()

    await executor.execute(FakeContext("Show invoices for customer id=7"), queue)

    assert agent.instructions == ["Show invoices for customer id=7"]
    payload = _event_payload(queue)
    assert payload["success"] is True
    assert payload["content"] == "invoice ok"


@pytest.mark.anyio
async def test_music_executor_prefers_generic_payload_instruction() -> None:
    executor = MusicAgentExecutor()
    agent = RecordingMusicAgent()
    executor.agent = agent
    queue = FakeEventQueue()

    context = FakeContext(
            "compatibility text",
            data={"instruction": "Recommend 5 Jazz songs."},
    )
    context.message.parts = ["fake-data-part"]

    from multi_agent_system.a2a_servers.music_agent import executor as music_executor

    original_get_data_parts = music_executor.get_data_parts
    music_executor.get_data_parts = lambda parts: [context.data]
    try:
        await executor.execute(context, queue)
    finally:
        music_executor.get_data_parts = original_get_data_parts

    assert agent.instructions == ["Recommend 5 Jazz songs."]
    payload = _event_payload(queue)
    assert payload["success"] is True
    assert payload["content"] == "music ok"


def _event_payload(queue: FakeEventQueue) -> dict:
    assert queue.events
    parts = queue.events[0].parts
    text = getattr(parts[0], "text", None)
    if text is None:
        text = parts[0].root.text
    return json.loads(text)
