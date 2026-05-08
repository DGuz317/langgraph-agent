import asyncio

from my_agent.utils import nodes
from my_agent.utils.state import AppState


class _FakePlannerService:
    async def plan(self, *, user_input: str):
        return [{"agent": "invoice_agent", "query": user_input}]


class _FakeTaskExecutionService:
    async def execute(self, *, task):
        return {
            "agent": task["agent"],
            "status": "success",
            "result": {"query": task["query"]},
            "error": None,
        }


class _FakeAggregatorService:
    async def aggregate(self, *, results):
        return f"handled {len(results)} results"


def test_state_typed_dict_supports_partial_updates():
    state: AppState = {"messages": [{"role": "user", "content": "hello"}]}

    assert state["messages"][0]["content"] == "hello"


def test_planner_node_uses_latest_user_message_without_duplication(monkeypatch):
    monkeypatch.setattr(nodes, "planner_service", _FakePlannerService())
    state: AppState = {
        "messages": [
            {"role": "user", "content": "first"},
            {"role": "assistant", "content": "ack"},
            {"role": "user", "content": "latest"},
        ]
    }

    result = asyncio.run(nodes.planner_node(state))

    assert result == {"tasks": [{"agent": "invoice_agent", "query": "latest"}]}
    assert state["messages"] == [
        {"role": "user", "content": "first"},
        {"role": "assistant", "content": "ack"},
        {"role": "user", "content": "latest"},
    ]


def test_execute_tasks_node_returns_empty_results_for_empty_plan():
    result = asyncio.run(nodes.execute_tasks_node({"tasks": []}))

    assert result == {"results": []}


def test_execute_tasks_node_executes_all_tasks(monkeypatch):
    monkeypatch.setattr(nodes, "task_execution_service", _FakeTaskExecutionService())
    state: AppState = {
        "tasks": [
            {"agent": "music_agent", "query": "tracks"},
            {"agent": "invoice_agent", "query": "invoices"},
        ]
    }

    result = asyncio.run(nodes.execute_tasks_node(state))

    assert result == {
        "results": [
            {
                "agent": "music_agent",
                "status": "success",
                "result": {"query": "tracks"},
                "error": None,
            },
            {
                "agent": "invoice_agent",
                "status": "success",
                "result": {"query": "invoices"},
                "error": None,
            },
        ]
    }


def test_aggregate_node_appends_assistant_message(monkeypatch):
    monkeypatch.setattr(nodes, "aggregator_service", _FakeAggregatorService())
    state: AppState = {
        "messages": [{"role": "user", "content": "latest"}],
        "results": [{"agent": "music_agent", "status": "success", "result": {}, "error": None}],
    }

    result = asyncio.run(nodes.aggregate_node(state))

    assert result == {
        "final_response": "handled 1 results",
        "messages": [
            {"role": "user", "content": "latest"},
            {"role": "assistant", "content": "handled 1 results"},
        ],
    }
