import pytest

from multi_agent_system.planner_app.nodes import invoice_node, music_node


@pytest.mark.anyio
async def test_invoice_node_returns_readable_failure_when_a2a_client_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingInvoiceClient:
        async def ask(self, text: str) -> str:
            raise RuntimeError("invoice service unavailable")

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.InvoiceA2AClient",
        FailingInvoiceClient,
    )

    result = await invoice_node(
        {
            "user_input": "Get latest invoice for customer_id=5",
            "planner_output": {
                "tasks": [
                    {
                        "agent": "invoice",
                        "instruction": "Get latest invoice for customer_id=5",
                        "missing_fields": [],
                        "status": "not_started",
                    }
                ]
            },
        }
    )

    assert result["planner_output"]["tasks"][0]["status"] == "failed"
    assert "Invoice task failed:" in result["invoice_result"]
    assert "invoice service unavailable" in result["invoice_result"]


@pytest.mark.anyio
async def test_music_node_returns_readable_failure_when_a2a_client_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingMusicClient:
        async def ask(self, text: str) -> str:
            raise RuntimeError("music service unavailable")

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.MusicA2AClient",
        FailingMusicClient,
    )

    result = await music_node(
        {
            "user_input": "Find tracks by artist AC/DC",
            "planner_output": {
                "tasks": [
                    {
                        "agent": "music",
                        "instruction": "Find tracks by artist AC/DC",
                        "missing_fields": [],
                        "status": "not_started",
                    }
                ]
            },
        }
    )

    assert result["planner_output"]["tasks"][0]["status"] == "failed"
    assert "Music task failed:" in result["music_result"]
    assert "music service unavailable" in result["music_result"]


@pytest.mark.anyio
async def test_invoice_node_fails_readably_when_instruction_is_missing() -> None:
    result = await invoice_node(
        {
            "user_input": "Get latest invoice",
            "planner_output": {
                "tasks": [
                    {
                        "agent": "invoice",
                        "instruction": "",
                        "missing_fields": [],
                        "status": "not_started",
                    }
                ]
            },
        }
    )

    assert result["planner_output"]["tasks"][0]["status"] == "failed"
    assert "missing an instruction" in result["invoice_result"]
