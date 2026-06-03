import pytest

from multi_agent_system.planner_app.edges import route_after_invoice, route_after_planner
from multi_agent_system.planner_app.graph import build_graph
from multi_agent_system.planner_app.nodes import (
    final_response_node,
    invoice_node,
    missing_info_node,
    music_node,
    planner_node,
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakePlannerOutput:
    def __init__(self, tasks: list[dict]) -> None:
        self.tasks = tasks
        self.missing_fields = [
            field
            for task in tasks
            for field in task.get("missing_fields", [])
        ]

    def model_dump(self) -> dict:
        return {
            "status": "completed",
            "tasks": self.tasks,
            "confidence": 1.0,
            "requires_aggregation": len(self.tasks) > 1,
            "missing_fields": self.missing_fields,
        }


class FakePlanner:
    def __init__(self, output: FakePlannerOutput) -> None:
        self.output = output
        self.calls: list[dict] = []

    async def ainvoke(self, user_input: str, *, memory_context: str | None = None):
        self.calls.append(
            {
                "user_input": user_input,
                "memory_context": memory_context,
            }
        )
        return self.output


@pytest.mark.anyio
async def test_route_after_planner_routes_by_agent() -> None:
    assert await route_after_planner(
        {"planner_output": {"tasks": [{"agent": "invoice"}]}}
    ) == "invoice"
    assert await route_after_planner(
        {"planner_output": {"tasks": [{"agent": "music"}]}}
    ) == "music"
    assert await route_after_planner(
        {"planner_output": {"tasks": [{"agent": "invoice"}, {"agent": "music"}]}}
    ) == "invoice"


@pytest.mark.anyio
async def test_route_after_planner_routes_missing_info() -> None:
    route = await route_after_planner(
        {
            "missing_fields": ["customer_id"],
            "planner_output": {"tasks": [{"agent": "invoice"}]},
        }
    )

    assert route == "missing_info"


@pytest.mark.anyio
async def test_route_after_invoice_runs_music_when_pending() -> None:
    route = await route_after_invoice(
        {
            "invoice_result": "ok",
            "planner_output": {
                "tasks": [
                    {"agent": "invoice", "status": "completed"},
                    {"agent": "music", "status": "not_started"},
                ]
            },
        }
    )

    assert route == "music"


@pytest.mark.anyio
async def test_planner_node_adds_missing_customer_id_before_dispatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.planner",
        FakePlanner(
            FakePlannerOutput(
                [
                    {
                        "agent": "invoice",
                        "instruction": "Show the latest invoice.",
                        "missing_fields": [],
                        "status": "not_started",
                    }
                ]
            )
        ),
    )

    result = await planner_node({"user_input": "latest invoice"})

    assert result["missing_fields"] == ["customer_id"]
    assert result["planner_output"]["tasks"][0]["missing_fields"] == ["customer_id"]
    assert await route_after_planner(result) == "missing_info"
    assert result["invoice_result"] is None
    assert result["music_result"] is None
    assert result["final_answer"] is None


@pytest.mark.anyio
async def test_planner_node_reuses_same_thread_invoice_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_planner = FakePlanner(
        FakePlannerOutput(
            [
                {
                    "agent": "invoice",
                    "instruction": "Get the support employee for each invoices.",
                    "missing_fields": [],
                    "status": "not_started",
                }
            ]
        )
    )
    monkeypatch.setattr("multi_agent_system.planner_app.nodes.planner", fake_planner)

    result = await planner_node(
        {
            "user_input": "Can you provide the support employee for each invoices?",
            "invoice_result": "old result",
            "music_result": "old music",
            "final_answer": "old answer",
            "invoice_context": {
                "customer_id": "1",
                "invoice_ids": ["382", "327"],
                "last_invoice_instruction": "Show 5 most recent invoices for customer id=1.",
            },
        }
    )

    instruction = result["planner_output"]["tasks"][0]["instruction"]
    assert "Previous same-thread invoice context: customer_id=1" in instruction
    assert "invoice_ids=382, 327" in instruction
    assert result["missing_fields"] == []
    assert "Recent same-thread invoice context" in fake_planner.calls[0]["memory_context"]
    assert result["invoice_result"] is None


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

    result = await invoice_node(
        {
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
    )

    assert captured == ["Show 3 most recent invoices for customer id=7."]
    assert result["planner_output"]["tasks"][0]["status"] == "completed"
    assert result["execution_evidence"][0]["operation"] == "agent_instruction"


@pytest.mark.anyio
async def test_invoice_node_stores_same_thread_invoice_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeInvoiceClient:
        async def ask(self, text: str) -> str:
            return (
                '{"success": true, "content": "1. Invoice ID: 382, Total: $8.91\\n'
                '2. Invoice ID: 327, Total: $13.86"}'
            )

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.InvoiceA2AClient",
        FakeInvoiceClient,
    )

    result = await invoice_node(
        {
            "user_input": "Show invoices",
            "customer_id": "1",
            "planner_output": {
                "tasks": [
                    {
                        "agent": "invoice",
                        "instruction": "Show 2 most recent invoices for customer id=1.",
                        "status": "not_started",
                        "missing_fields": [],
                    }
                ]
            },
        }
    )

    assert result["invoice_context"] == {
        "customer_id": "1",
        "invoice_ids": ["382", "327"],
        "last_invoice_instruction": "Show 2 most recent invoices for customer id=1.",
    }


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

    result = await music_node(
        {
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
    )

    assert captured == ["Recommend 5 Jazz songs."]
    assert result["planner_output"]["tasks"][0]["status"] == "completed"


@pytest.mark.anyio
async def test_final_response_node_uses_aggregator_for_no_task_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeAggregator:
        async def ainvoke(self, data):
            assert data.user_input == "Hello, what can you do?"
            assert data.results == []
            return type("Output", (), {"final_answer": "LLM generated capabilities."})()

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.aggregator",
        FakeAggregator(),
    )

    result = await final_response_node(
        {
            "user_input": "Hello, what can you do?",
            "planner_output": {"tasks": []},
            "execution_evidence": [],
        }
    )

    assert result["final_answer"] == "LLM generated capabilities."
    assert result["execution_evidence"][0]["operation"] == "general_response"


@pytest.mark.anyio
async def test_missing_info_node_appends_resume_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.interrupt_for_missing_info",
        lambda missing_fields: {"genre": "Jazz"},
    )

    result = await missing_info_node(
        {
            "missing_fields": ["genre"],
            "planner_output": {
                "tasks": [
                    {
                        "agent": "music",
                        "instruction": "Recommend 5 songs.",
                        "missing_fields": ["genre"],
                        "status": "not_started",
                    }
                ]
            },
        }
    )

    task = result["planner_output"]["tasks"][0]
    assert "genre=Jazz" in task["instruction"]
    assert result["missing_fields"] == []


@pytest.mark.anyio
async def test_missing_info_node_appends_customer_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_interrupt_for_missing_info(missing_fields: list[str]) -> dict:
        assert missing_fields == ["customer_id"]
        return {"customer_id": "7"}

    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.interrupt_for_missing_info",
        fake_interrupt_for_missing_info,
    )

    result = await missing_info_node(
        {
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
    )
    task = result["planner_output"]["tasks"][0]

    assert "Additional user-provided information: customer_id=7." in task["instruction"]
    assert task["missing_fields"] == []


@pytest.mark.anyio
async def test_missing_info_node_keeps_unresolved_fields_when_resume_is_unparsed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.interrupt_for_missing_info",
        lambda missing_fields: {},
    )

    result = await missing_info_node(
        {
            "missing_fields": ["customer_id"],
            "planner_output": {
                "tasks": [
                    {
                        "agent": "invoice",
                        "instruction": "Show the latest invoice.",
                        "missing_fields": ["customer_id"],
                        "status": "not_started",
                    }
                ]
            },
        }
    )

    assert result["missing_fields"] == ["customer_id"]
    assert result["planner_output"]["tasks"][0]["missing_fields"] == ["customer_id"]
    assert await route_after_planner(result) == "missing_info"


@pytest.mark.anyio
async def test_graph_dispatches_multi_agent_natural_language_tasks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from multi_agent_system.planner_app import nodes

    captured = {"invoice": [], "music": []}

    class FakeInvoiceClient:
        async def ask(self, text: str) -> str:
            captured["invoice"].append(text)
            return '{"success": true, "content": "invoice ok"}'

    class FakeMusicClient:
        async def ask(self, text: str) -> str:
            captured["music"].append(text)
            return '{"success": true, "content": "music ok"}'

    monkeypatch.setattr(nodes, "InvoiceA2AClient", FakeInvoiceClient)
    monkeypatch.setattr(nodes, "MusicA2AClient", FakeMusicClient)
    monkeypatch.setattr(
        nodes,
        "planner",
        FakePlanner(
            FakePlannerOutput(
                [
                    {
                        "agent": "invoice",
                        "instruction": "Show 3 most recent invoices for customer id=7.",
                        "missing_fields": [],
                        "status": "not_started",
                    },
                    {
                        "agent": "music",
                        "instruction": "Recommend 5 Jazz songs.",
                        "missing_fields": [],
                        "status": "not_started",
                    },
                ]
            )
        ),
    )

    graph = build_graph()
    result = await graph.ainvoke(
        {"user_input": "Show invoices and recommend music"},
        config={"configurable": {"thread_id": "e2e-natural-language"}},
    )

    assert captured == {
        "invoice": ["Show 3 most recent invoices for customer id=7."],
        "music": ["Recommend 5 Jazz songs."],
    }
    assert "Invoice Agent result" in result["final_answer"]
    assert "Music Agent result" in result["final_answer"]
