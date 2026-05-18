import pytest

from multi_agent_system.planner_app.nodes import (
    invoice_node,
    music_node,
)


@pytest.mark.anyio
async def test_invoice_node_returns_readable_failure_when_a2a_client_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingInvoiceClient:
        async def ask(self, instruction: str) -> str:
            raise RuntimeError("invoice service unavailable")

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.InvoiceA2AClient",
        FailingInvoiceClient,
    )

    state = {
        "user_input": "Get latest invoice for customer_id=5",
        "planner_output": {
            "tasks": [
                {
                    "id": "1",
                    "agent": "invoice",
                    "intent": "latest_invoice",
                    "args": {"customer_id": "5"},
                    "instruction": "",
                    "missing_fields": [],
                    "status": "not_started",
                }
            ],
            "requires_aggregation": False,
            "missing_fields": [],
            "confidence": 1.0,
            "status": "completed",
        },
    }

    result = await invoice_node(state)

    assert result["planner_output"]["tasks"][0]["status"] == "failed"
    assert "Invoice task failed:" in result["invoice_result"]
    assert "invoice service unavailable" in result["invoice_result"]


@pytest.mark.anyio
async def test_music_node_returns_readable_failure_when_a2a_client_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingMusicClient:
        async def ask(self, instruction: str) -> str:
            raise RuntimeError("music service unavailable")

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.MusicA2AClient",
        FailingMusicClient,
    )

    state = {
        "user_input": "Find tracks by artist AC/DC",
        "planner_output": {
            "tasks": [
                {
                    "id": "1",
                    "agent": "music",
                    "intent": "tracks_by_artist",
                    "args": {"artist": "AC/DC"},
                    "instruction": "",
                    "missing_fields": [],
                    "status": "not_started",
                }
            ],
            "requires_aggregation": False,
            "missing_fields": [],
            "confidence": 1.0,
            "status": "completed",
        },
    }

    result = await music_node(state)

    assert result["planner_output"]["tasks"][0]["status"] == "failed"
    assert "Music task failed:" in result["music_result"]
    assert "music service unavailable" in result["music_result"]


@pytest.mark.anyio
async def test_invoice_node_returns_readable_failure_when_no_pending_task() -> None:
    state = {
        "user_input": "Get latest invoice for customer_id=5",
        "planner_output": {
            "tasks": [
                {
                    "id": "1",
                    "agent": "invoice",
                    "intent": "latest_invoice",
                    "args": {"customer_id": "5"},
                    "instruction": "Get latest invoice for customer_id=5",
                    "missing_fields": [],
                    "status": "completed",
                }
            ],
            "requires_aggregation": False,
            "missing_fields": [],
            "confidence": 1.0,
            "status": "completed",
        },
    }

    result = await invoice_node(state)

    assert "Invoice task failed:" in result["invoice_result"]
    assert "No pending task found for agent: invoice" in result["invoice_result"]


@pytest.mark.anyio
async def test_music_node_returns_readable_failure_when_no_pending_task() -> None:
    state = {
        "user_input": "Find tracks by artist AC/DC",
        "planner_output": {
            "tasks": [
                {
                    "id": "1",
                    "agent": "music",
                    "intent": "tracks_by_artist",
                    "args": {"artist": "AC/DC"},
                    "instruction": "Find tracks by artist AC/DC",
                    "missing_fields": [],
                    "status": "completed",
                }
            ],
            "requires_aggregation": False,
            "missing_fields": [],
            "confidence": 1.0,
            "status": "completed",
        },
    }

    result = await music_node(state)

    assert "Music task failed:" in result["music_result"]
    assert "No pending task found for agent: music" in result["music_result"]


@pytest.mark.anyio
async def test_invoice_node_fails_readably_when_instruction_building_fails() -> None:
    state = {
        "user_input": "Get latest invoice",
        "planner_output": {
            "tasks": [
                {
                    "id": "1",
                    "agent": "invoice",
                    "intent": "latest_invoice",
                    "args": {},
                    "instruction": "",
                    "missing_fields": [],
                    "status": "not_started",
                }
            ],
            "requires_aggregation": False,
            "missing_fields": [],
            "confidence": 1.0,
            "status": "completed",
        },
    }

    result = await invoice_node(state)

    assert result["planner_output"]["tasks"][0]["status"] == "failed"
    assert "Invoice task failed:" in result["invoice_result"]
    assert "customer_id" in result["invoice_result"]
