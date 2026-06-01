import pytest

from multi_agent_system.planner_app.graph import build_graph


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

    async def ainvoke(self, user_input: str, *, memory_context: str | None = None):
        return self.output


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
