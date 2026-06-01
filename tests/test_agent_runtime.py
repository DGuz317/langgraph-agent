import pytest

from langchain_core.messages import AIMessage

from multi_agent_system.common.agent_runtime import (
    AgentRunResult,
    LangChainAgentRuntime,
)
from multi_agent_system.common.execution_evidence import collect_execution_evidence


class FakeCompiledAgent:
    async def ainvoke(self, payload):
        return {"messages": [*payload["messages"], AIMessage(content="done")]}


@pytest.mark.anyio
async def test_langchain_runtime_invokes_created_agent(monkeypatch) -> None:
    created = {}

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
    assert created == {}


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
