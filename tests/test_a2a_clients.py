import pytest


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_invoice_client_get_latest_invoice_builds_expected_instruction(monkeypatch) -> None:
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
async def test_music_client_get_tracks_by_artist_builds_expected_instruction(monkeypatch) -> None:
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
