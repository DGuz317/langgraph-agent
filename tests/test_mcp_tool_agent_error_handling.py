import asyncio

import pytest

from multi_agent_system.common.errors import MCPToolError
from multi_agent_system.common.execution_evidence import collect_execution_evidence
from multi_agent_system.common.mcp_tool_agent import MCPToolAgent


class FakeTool:
    def __init__(
        self,
        name: str,
        result=None,
        error: Exception | None = None,
    ) -> None:
        self.name = name
        self.result = result
        self.error = error
        self.last_args = None

    async def ainvoke(self, args: dict):
        self.last_args = args

        if self.error is not None:
            raise self.error

        return self.result


class FakeClient:
    def __init__(
        self,
        tools=None,
        error: Exception | None = None,
    ) -> None:
        self.tools = tools or []
        self.error = error

    async def get_tools(self):
        if self.error is not None:
            raise self.error

        return self.tools


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_call_tool_returns_parsed_text_payload() -> None:
    tool = FakeTool(
        name="get_items",
        result=[{"type": "text", "text": "[{\"id\": 1}]"}],
    )
    agent = MCPToolAgent(client=FakeClient(tools=[tool]))

    result = await agent.call_tool("get_items", {"customer_id": "5"})

    assert result == [{"id": 1}]
    assert tool.last_args == {"customer_id": "5"}


@pytest.mark.anyio
async def test_call_tool_records_sanitized_execution_evidence() -> None:
    tool = FakeTool(
        name="get_items",
        result=[{"type": "text", "text": "[{\"private\": \"value\"}]"}],
    )
    agent = MCPToolAgent(client=FakeClient(tools=[tool]))
    agent.evidence_agent = "invoice"

    with collect_execution_evidence() as evidence:
        await agent.call_tool("get_items", {"customer_id": "5"})

    assert [item.kind for item in evidence] == ["mcp_tool_call", "mcp_tool_result"]
    assert evidence[0].fields == ["customer_id"]
    assert "5" not in evidence[0].summary
    assert "private" not in evidence[1].summary


@pytest.mark.anyio
async def test_call_tool_records_sanitized_failure_evidence() -> None:
    tool = FakeTool(name="get_items", error=RuntimeError("private failure details"))
    agent = MCPToolAgent(client=FakeClient(tools=[tool]))
    agent.evidence_agent = "invoice"

    with collect_execution_evidence() as evidence:
        with pytest.raises(MCPToolError):
            await agent.call_tool("get_items", {"customer_id": "5"})

    assert evidence[-1].status == "failed"
    assert "private failure details" not in evidence[-1].summary


@pytest.mark.anyio
async def test_evidence_collection_is_isolated_for_concurrent_calls() -> None:
    async def collect_for(field: str) -> list[str]:
        agent = MCPToolAgent(
            client=FakeClient(
                tools=[FakeTool(name="get_items", result=[])],
            )
        )
        with collect_execution_evidence() as evidence:
            await agent.call_tool("get_items", {field: "private"})
        return evidence[0].fields

    first, second = await asyncio.gather(
        collect_for("customer_id"),
        collect_for("invoice_id"),
    )

    assert first == ["customer_id"]
    assert second == ["invoice_id"]


@pytest.mark.anyio
async def test_call_tool_returns_empty_list_payload() -> None:
    tool = FakeTool(
        name="get_items",
        result=[],
    )
    agent = MCPToolAgent(client=FakeClient(tools=[tool]))

    result = await agent.call_tool("get_items", {})

    assert result == []


@pytest.mark.anyio
async def test_call_tool_returns_structured_content() -> None:
    tool = FakeTool(
        name="get_items",
        result={
            "structuredContent": {
                "items": [{"id": 1}],
            }
        },
    )
    agent = MCPToolAgent(client=FakeClient(tools=[tool]))

    result = await agent.call_tool("get_items", {})

    assert result == {"items": [{"id": 1}]}


@pytest.mark.anyio
async def test_call_tool_raises_when_tool_loader_fails() -> None:
    agent = MCPToolAgent(client=FakeClient(error=RuntimeError("server down")))

    with pytest.raises(MCPToolError, match="Failed to load MCP tools"):
        await agent.call_tool("get_items", {})


@pytest.mark.anyio
async def test_call_tool_raises_when_tool_not_found() -> None:
    agent = MCPToolAgent(
        client=FakeClient(
            tools=[
                FakeTool(name="other_tool", result=[]),
            ]
        )
    )

    with pytest.raises(MCPToolError, match="was not found"):
        await agent.call_tool("get_items", {})


@pytest.mark.anyio
async def test_call_tool_raises_when_tool_invocation_fails() -> None:
    tool = FakeTool(
        name="get_items",
        error=RuntimeError("tool exploded"),
    )
    agent = MCPToolAgent(client=FakeClient(tools=[tool]))

    with pytest.raises(MCPToolError, match="invocation failed"):
        await agent.call_tool("get_items", {})


@pytest.mark.anyio
async def test_call_tool_raises_when_text_payload_is_invalid_json() -> None:
    tool = FakeTool(
        name="get_items",
        result=[{"type": "text", "text": "{invalid json"}],
    )
    agent = MCPToolAgent(client=FakeClient(tools=[tool]))

    with pytest.raises(MCPToolError, match="invalid JSON text"):
        await agent.call_tool("get_items", {})


@pytest.mark.anyio
async def test_call_tool_raises_when_result_type_is_unsupported() -> None:
    tool = FakeTool(
        name="get_items",
        result=123,
    )
    agent = MCPToolAgent(client=FakeClient(tools=[tool]))

    with pytest.raises(MCPToolError, match="unsupported result type"):
        await agent.call_tool("get_items", {})
