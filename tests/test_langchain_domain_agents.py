import pytest

from langchain_core.messages import AIMessage

from multi_agent_system.a2a_servers.invoice_agent.agent import InvoiceAgent
from multi_agent_system.a2a_servers.music_agent.agent import MusicAgent
from multi_agent_system.common.agent_runtime import (
    AgentRunResult,
    LangChainAgentRuntime,
)
from multi_agent_system.common.execution_evidence import collect_execution_evidence


class FakeCompiledAgent:
    async def ainvoke(self, payload):
        return {"messages": [*payload["messages"], AIMessage(content="done")]}


class RecordingRuntime:
    def __init__(self, content: str) -> None:
        self.instructions: list[str] = []
        self.result = AgentRunResult(success=True, content=content)

    async def ainvoke(self, instruction: str) -> AgentRunResult:
        self.instructions.append(instruction)
        return self.result


class FailingRuntime:
    async def ainvoke(self, instruction: str) -> AgentRunResult:
        raise RuntimeError("runtime unavailable")


@pytest.mark.anyio
async def test_langchain_runtime_invokes_created_agent(monkeypatch) -> None:
    async def fake_get_agent(self):
        return FakeCompiledAgent()

    monkeypatch.setattr(LangChainAgentRuntime, "_get_agent", fake_get_agent)
    runtime = LangChainAgentRuntime(
        agent_name="music",
        system_prompt="music prompt",
        allowed_tools={"get_songs_by_genre"},
    )

    result = await runtime.ainvoke("Recommend 5 Jazz songs.")

    assert isinstance(result, AgentRunResult)
    assert result.success is True
    assert result.content == "done"
    assert result.messages


@pytest.mark.anyio
async def test_runtime_records_mcp_tool_evidence() -> None:
    runtime = LangChainAgentRuntime(
        agent_name="invoice",
        system_prompt="invoice prompt",
        allowed_tools={"query_invoice_database"},
    )

    async def handler(request):
        return type(
            "Result",
            (),
            {"structuredContent": {"result": [{"InvoiceId": 1}]}},
        )()

    request = type(
        "Request",
        (),
        {
            "name": "query_invoice_database",
            "args": {"sql_query": "SELECT InvoiceId FROM Invoice LIMIT 1"},
        },
    )()

    with collect_execution_evidence() as evidence:
        await runtime._record_tool_evidence(request, handler)

    assert [item.kind for item in evidence] == ["mcp_tool_call", "mcp_tool_result"]
    assert evidence[0].arguments == {
        "sql_query": "SELECT InvoiceId FROM Invoice LIMIT 1"
    }
    assert "1 record" in evidence[1].summary


@pytest.mark.anyio
async def test_runtime_rejects_missing_required_tool_arg_before_mcp_call() -> None:
    runtime = LangChainAgentRuntime(
        agent_name="invoice",
        system_prompt="invoice prompt",
        allowed_tools={"get_invoices_by_customer_sorted_by_date"},
        required_tool_args={
            "get_invoices_by_customer_sorted_by_date": {"customer_id"},
        },
    )
    handler_called = False

    async def handler(request):
        nonlocal handler_called
        handler_called = True

    request = type(
        "Request",
        (),
        {
            "name": "get_invoices_by_customer_sorted_by_date",
            "args": {"customer_id": None},
            "server_name": "default",
            "headers": None,
            "runtime": None,
        },
    )()

    with collect_execution_evidence() as evidence:
        with pytest.raises(ValueError, match="customer_id"):
            await runtime._record_tool_evidence(request, handler)

    assert handler_called is False
    assert [item.kind for item in evidence] == ["mcp_tool_call", "mcp_tool_result"]
    assert evidence[1].status == "failed"
    assert "customer_id" in evidence[1].summary


@pytest.mark.anyio
async def test_runtime_normalizes_required_tool_arg_to_string() -> None:
    runtime = LangChainAgentRuntime(
        agent_name="invoice",
        system_prompt="invoice prompt",
        allowed_tools={"get_invoices_by_customer_sorted_by_date"},
        required_tool_args={
            "get_invoices_by_customer_sorted_by_date": {"customer_id"},
        },
    )
    captured_args = {}

    async def handler(request):
        captured_args.update(request.args)
        return type("Result", (), {"structuredContent": {"result": []}})()

    request = type(
        "Request",
        (),
        {
            "name": "get_invoices_by_customer_sorted_by_date",
            "args": {"customer_id": 5},
            "server_name": "default",
            "headers": None,
            "runtime": None,
        },
    )()

    with collect_execution_evidence() as evidence:
        await runtime._record_tool_evidence(request, handler)

    assert captured_args == {"customer_id": "5"}
    assert evidence[0].arguments == {"customer_id": "5"}
    assert evidence[1].status == "completed"


@pytest.mark.anyio
async def test_invoice_agent_delegates_instruction_to_runtime() -> None:
    runtime = RecordingRuntime("Invoice answer.")
    agent = InvoiceAgent(runtime=runtime)

    response = await agent.ainvoke("Show 3 most recent invoices for customer id=7.")

    assert response.success is True
    assert response.content == "Invoice answer."
    assert runtime.instructions == ["Show 3 most recent invoices for customer id=7."]


@pytest.mark.anyio
async def test_invoice_agent_returns_runtime_failure() -> None:
    agent = InvoiceAgent(runtime=FailingRuntime())

    response = await agent.ainvoke("Show invoices.")

    assert response.success is False
    assert "runtime unavailable" in response.content


@pytest.mark.anyio
async def test_music_agent_delegates_instruction_to_runtime() -> None:
    runtime = RecordingRuntime("Music answer.")
    agent = MusicAgent(runtime=runtime)

    response = await agent.ainvoke("Recommend 5 Jazz songs.")

    assert response.success is True
    assert response.content == "Music answer."
    assert runtime.instructions == ["Recommend 5 Jazz songs."]


@pytest.mark.anyio
async def test_music_agent_returns_runtime_failure() -> None:
    agent = MusicAgent(runtime=FailingRuntime())

    response = await agent.ainvoke("Recommend songs.")

    assert response.success is False
    assert "runtime unavailable" in response.content
