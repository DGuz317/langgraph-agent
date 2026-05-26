import pytest

from multi_agent_system.planner_app.nodes import (
    invoice_node,
    music_node,
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_invoice_node_rebuilds_instruction_from_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    class FakeInvoiceClient:
        async def ask_payload(self, payload: dict) -> str:
            captured["instruction"] = payload["instruction"]
            captured["payload"] = payload
            return '{"success": true, "content": "ok", "data": {}}'

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.InvoiceA2AClient",
        FakeInvoiceClient,
    )

    state = {
        "user_input": "Get latest invoice for customer_id=5",
        "planner_output": {
            "status": "completed",
            "confidence": 1.0,
            "requires_aggregation": False,
            "missing_fields": [],
            "tasks": [
                {
                    "id": "task-1",
                    "agent": "invoice",
                    "intent": "latest_invoice",
                    "instruction": "stale instruction should not be used",
                    "args": {"customer_id": "5"},
                    "missing_fields": [],
                    "status": "not_started",
                }
            ],
        },
    }

    result = await invoice_node(state)

    assert captured["instruction"] == "Get latest invoice for customer_id=5"
    assert (
        result["planner_output"]["tasks"][0]["instruction"]
        == "Get latest invoice for customer_id=5"
    )
    assert result["planner_output"]["tasks"][0]["a2a_payload"] == {
        "agent": "invoice",
        "intent": "latest_invoice",
        "args": {"customer_id": "5"},
        "instruction": "Get latest invoice for customer_id=5",
    }
    assert captured["payload"] == result["planner_output"]["tasks"][0]["a2a_payload"]
    assert result["planner_output"]["tasks"][0]["status"] == "completed"


@pytest.mark.anyio
async def test_invoice_node_rebuilds_invoice_detail_payload_from_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, dict] = {}

    class FakeInvoiceClient:
        async def ask_payload(self, payload: dict) -> str:
            captured["payload"] = payload
            return '{"success": true, "content": "ok", "data": {}}'

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.InvoiceA2AClient",
        FakeInvoiceClient,
    )

    state = {
        "user_input": "Show invoice detail for invoice_id=361",
        "planner_output": {
            "status": "completed",
            "confidence": 1.0,
            "requires_aggregation": False,
            "missing_fields": [],
            "tasks": [
                {
                    "id": "task-1",
                    "agent": "invoice",
                    "intent": "invoice_detail",
                    "instruction": "stale instruction should not be used",
                    "args": {"invoice_id": "361"},
                    "missing_fields": [],
                    "status": "not_started",
                }
            ],
        },
    }

    result = await invoice_node(state)

    assert captured["payload"] == {
        "agent": "invoice",
        "intent": "invoice_detail",
        "args": {"invoice_id": "361"},
        "instruction": "Get invoice detail for invoice_id=361",
    }
    assert result["planner_output"]["tasks"][0]["a2a_payload"] == captured["payload"]


@pytest.mark.anyio
async def test_invoice_node_rebuilds_invoice_summary_payload_from_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, dict] = {}

    class FakeInvoiceClient:
        async def ask_payload(self, payload: dict) -> str:
            captured["payload"] = payload
            return '{"success": true, "content": "ok", "data": {}}'

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.InvoiceA2AClient",
        FakeInvoiceClient,
    )

    state = {
        "user_input": "Show total invoice spending for customer_id=5",
        "planner_output": {
            "status": "completed",
            "confidence": 1.0,
            "requires_aggregation": False,
            "missing_fields": [],
            "tasks": [
                {
                    "id": "task-1",
                    "agent": "invoice",
                    "intent": "invoice_summary",
                    "instruction": "stale instruction should not be used",
                    "args": {"customer_id": "5"},
                    "missing_fields": [],
                    "status": "not_started",
                }
            ],
        },
    }

    result = await invoice_node(state)

    assert captured["payload"] == {
        "agent": "invoice",
        "intent": "invoice_summary",
        "args": {"customer_id": "5"},
        "instruction": "Get invoice summary for customer_id=5",
    }
    assert result["planner_output"]["tasks"][0]["a2a_payload"] == captured["payload"]


@pytest.mark.anyio
async def test_invoice_node_rebuilds_customer_support_employee_payload_from_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, dict] = {}

    class FakeInvoiceClient:
        async def ask_payload(self, payload: dict) -> str:
            captured["payload"] = payload
            return '{"success": true, "content": "ok", "data": {}}'

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.InvoiceA2AClient",
        FakeInvoiceClient,
    )

    state = {
        "user_input": "Who is my support employee for customer_id=5?",
        "planner_output": {
            "status": "completed",
            "confidence": 1.0,
            "requires_aggregation": False,
            "missing_fields": [],
            "tasks": [
                {
                    "id": "task-1",
                    "agent": "invoice",
                    "intent": "customer_support_employee",
                    "instruction": "stale instruction should not be used",
                    "args": {"customer_id": "5"},
                    "missing_fields": [],
                    "status": "not_started",
                }
            ],
        },
    }

    result = await invoice_node(state)

    assert captured["payload"] == {
        "agent": "invoice",
        "intent": "customer_support_employee",
        "args": {"customer_id": "5"},
        "instruction": "Get support employee for customer_id=5",
    }
    assert result["planner_output"]["tasks"][0]["a2a_payload"] == captured["payload"]


@pytest.mark.anyio
async def test_invoice_node_rebuilds_unit_price_instruction_from_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    class FakeInvoiceClient:
        async def ask_payload(self, payload: dict) -> str:
            captured["instruction"] = payload["instruction"]
            return '{"success": true, "content": "ok", "data": []}'

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.InvoiceA2AClient",
        FakeInvoiceClient,
    )

    state = {
        "user_input": "Show invoices sorted by unit price for customer_id=5",
        "planner_output": {
            "status": "completed",
            "confidence": 1.0,
            "requires_aggregation": False,
            "missing_fields": [],
            "tasks": [
                {
                    "id": "task-1",
                    "agent": "invoice",
                    "intent": "invoices_by_unit_price",
                    "instruction": "stale instruction should not be used",
                    "args": {"customer_id": "5"},
                    "missing_fields": [],
                    "status": "not_started",
                }
            ],
        },
    }

    result = await invoice_node(state)

    assert (
        captured["instruction"]
        == "Get invoices sorted by unit price for customer_id=5"
    )
    assert (
        result["planner_output"]["tasks"][0]["instruction"]
        == "Get invoices sorted by unit price for customer_id=5"
    )


@pytest.mark.anyio
async def test_invoice_node_rebuilds_all_invoices_instruction_from_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    class FakeInvoiceClient:
        async def ask_payload(self, payload: dict) -> str:
            captured["instruction"] = payload["instruction"]
            return '{"success": true, "content": "ok", "data": []}'

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.InvoiceA2AClient",
        FakeInvoiceClient,
    )

    state = {
        "user_input": "All my invoice information of customer id 5",
        "planner_output": {
            "status": "completed",
            "confidence": 1.0,
            "requires_aggregation": False,
            "missing_fields": [],
            "tasks": [
                {
                    "id": "task-1",
                    "agent": "invoice",
                    "intent": "all_invoices",
                    "instruction": "stale instruction should not be used",
                    "args": {"customer_id": "5"},
                    "missing_fields": [],
                    "status": "not_started",
                }
            ],
        },
    }

    result = await invoice_node(state)

    assert captured["instruction"] == "Get all invoices for customer_id=5"
    assert result["planner_output"]["tasks"][0]["a2a_payload"] == {
        "agent": "invoice",
        "intent": "all_invoices",
        "args": {"customer_id": "5"},
        "instruction": "Get all invoices for customer_id=5",
    }


@pytest.mark.anyio
async def test_invoice_node_rebuilds_support_employee_instruction_from_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    class FakeInvoiceClient:
        async def ask_payload(self, payload: dict) -> str:
            captured["instruction"] = payload["instruction"]
            return '{"success": true, "content": "ok", "data": {}}'

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.InvoiceA2AClient",
        FakeInvoiceClient,
    )

    state = {
        "user_input": "Who supports latest invoice for customer_id=5?",
        "planner_output": {
            "status": "completed",
            "confidence": 1.0,
            "requires_aggregation": False,
            "missing_fields": [],
            "tasks": [
                {
                    "id": "task-1",
                    "agent": "invoice",
                    "intent": "latest_invoice_support_employee",
                    "instruction": "stale instruction should not be used",
                    "args": {"customer_id": "5"},
                    "missing_fields": [],
                    "status": "not_started",
                }
            ],
        },
    }

    result = await invoice_node(state)

    assert (
        captured["instruction"]
        == "Get support employee for latest invoice for customer_id=5"
    )
    assert result["planner_output"]["tasks"][0]["a2a_payload"] == {
        "agent": "invoice",
        "intent": "latest_invoice_support_employee",
        "args": {"customer_id": "5"},
        "instruction": "Get support employee for latest invoice for customer_id=5",
    }


@pytest.mark.anyio
async def test_music_node_rebuilds_genre_instruction_from_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    class FakeMusicClient:
        async def ask_payload(self, payload: dict) -> str:
            captured["instruction"] = payload["instruction"]
            return '{"success": true, "content": "ok", "data": []}'

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.MusicA2AClient",
        FakeMusicClient,
    )

    state = {
        "user_input": "Recommend some songs",
        "planner_output": {
            "status": "completed",
            "confidence": 1.0,
            "requires_aggregation": False,
            "missing_fields": [],
            "tasks": [
                {
                    "id": "task-1",
                    "agent": "music",
                    "intent": "songs_by_genre",
                    "instruction": "stale instruction should not be used",
                    "args": {"genre": "Jazz"},
                    "missing_fields": [],
                    "status": "not_started",
                }
            ],
        },
    }

    result = await music_node(state)

    assert captured["instruction"] == "Recommend songs by genre Jazz"
    assert (
        result["planner_output"]["tasks"][0]["instruction"]
        == "Recommend songs by genre Jazz"
    )
    assert result["planner_output"]["tasks"][0]["a2a_payload"] == {
        "agent": "music",
        "intent": "songs_by_genre",
        "args": {"genre": "Jazz"},
        "instruction": "Recommend songs by genre Jazz",
    }
    assert result["planner_output"]["tasks"][0]["status"] == "completed"


@pytest.mark.anyio
async def test_music_node_rebuilds_artist_instruction_from_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    class FakeMusicClient:
        async def ask_payload(self, payload: dict) -> str:
            captured["instruction"] = payload["instruction"]
            return '{"success": true, "content": "ok", "data": []}'

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.MusicA2AClient",
        FakeMusicClient,
    )

    state = {
        "user_input": "Find tracks by artist AC/DC",
        "planner_output": {
            "status": "completed",
            "confidence": 1.0,
            "requires_aggregation": False,
            "missing_fields": [],
            "tasks": [
                {
                    "id": "task-1",
                    "agent": "music",
                    "intent": "tracks_by_artist",
                    "instruction": "stale instruction should not be used",
                    "args": {"artist": "AC/DC"},
                    "missing_fields": [],
                    "status": "not_started",
                }
            ],
        },
    }

    result = await music_node(state)

    assert captured["instruction"] == "Find tracks by artist AC/DC"
    assert (
        result["planner_output"]["tasks"][0]["instruction"]
        == "Find tracks by artist AC/DC"
    )


@pytest.mark.anyio
async def test_music_node_rebuilds_song_check_instruction_from_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    class FakeMusicClient:
        async def ask_payload(self, payload: dict) -> str:
            captured["instruction"] = payload["instruction"]
            return '{"success": true, "content": "ok", "data": []}'

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.MusicA2AClient",
        FakeMusicClient,
    )

    state = {
        "user_input": "Check for song Ligia",
        "planner_output": {
            "status": "completed",
            "confidence": 1.0,
            "requires_aggregation": False,
            "missing_fields": [],
            "tasks": [
                {
                    "id": "task-1",
                    "agent": "music",
                    "intent": "check_song",
                    "instruction": "stale instruction should not be used",
                    "args": {"song_title": "Ligia"},
                    "missing_fields": [],
                    "status": "not_started",
                }
            ],
        },
    }

    result = await music_node(state)

    assert captured["instruction"] == "Check for song Ligia"
    assert (
        result["planner_output"]["tasks"][0]["instruction"]
        == "Check for song Ligia"
    )


@pytest.mark.anyio
async def test_node_instruction_rebuild_does_not_mutate_original_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeInvoiceClient:
        async def ask_payload(self, payload: dict) -> str:
            return '{"success": true, "content": "ok", "data": {}}'

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.InvoiceA2AClient",
        FakeInvoiceClient,
    )

    original_task = {
        "id": "task-1",
        "agent": "invoice",
        "intent": "latest_invoice",
        "instruction": "stale instruction should remain in original state",
        "args": {"customer_id": "5"},
        "missing_fields": [],
        "status": "not_started",
    }

    state = {
        "user_input": "Get latest invoice for customer_id=5",
        "planner_output": {
            "status": "completed",
            "confidence": 1.0,
            "requires_aggregation": False,
            "missing_fields": [],
            "tasks": [original_task],
        },
    }

    result = await invoice_node(state)

    assert original_task["instruction"] == "stale instruction should remain in original state"
    assert original_task["status"] == "not_started"
    assert result["planner_output"]["tasks"][0]["status"] == "completed"
