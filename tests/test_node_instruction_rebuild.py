import pytest

from multi_agent_system.planner_app.nodes import invoice_node, missing_info_node, music_node


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_invoice_node_dispatches_instruction_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[str] = []

    class FakeInvoiceClient:
        async def ask(self, text: str) -> str:
            captured.append(text)
            return '{"success": true, "content": "invoice ok"}'

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.InvoiceA2AClient",
        FakeInvoiceClient,
    )

    state = {
        "user_input": "Show invoices",
        "planner_output": {
            "tasks": [
                {
                    "agent": "invoice",
                    "instruction": "Show 3 most recent invoices for customer id=7.",
                    "status": "not_started",
                    "missing_fields": [],
                }
            ]
        },
    }

    result = await invoice_node(state)

    assert captured == ["Show 3 most recent invoices for customer id=7."]
    assert result["planner_output"]["tasks"][0]["status"] == "completed"
    assert result["execution_evidence"][0]["operation"] == "agent_instruction"


@pytest.mark.anyio
async def test_music_node_dispatches_instruction_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[str] = []

    class FakeMusicClient:
        async def ask(self, text: str) -> str:
            captured.append(text)
            return '{"success": true, "content": "music ok"}'

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.MusicA2AClient",
        FakeMusicClient,
    )

    state = {
        "user_input": "Recommend Jazz songs",
        "planner_output": {
            "tasks": [
                {
                    "agent": "music",
                    "instruction": "Recommend 5 Jazz songs.",
                    "status": "not_started",
                    "missing_fields": [],
                }
            ]
        },
    }

    result = await music_node(state)

    assert captured == ["Recommend 5 Jazz songs."]
    assert result["planner_output"]["tasks"][0]["status"] == "completed"


@pytest.mark.anyio
async def test_missing_info_appends_user_supplied_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_interrupt_for_missing_info(missing_fields: list[str]) -> dict:
        assert missing_fields == ["customer_id"]
        return {"customer_id": "7"}

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.interrupt_for_missing_info",
        fake_interrupt_for_missing_info,
    )

    state = {
        "missing_fields": ["customer_id"],
        "planner_output": {
            "tasks": [
                {
                    "agent": "invoice",
                    "instruction": "Show the most recent invoice.",
                    "missing_fields": ["customer_id"],
                    "status": "not_started",
                }
            ]
        },
    }

    result = await missing_info_node(state)
    task = result["planner_output"]["tasks"][0]

    assert "Additional user-provided information: customer_id=7." in task["instruction"]
    assert task["missing_fields"] == []
