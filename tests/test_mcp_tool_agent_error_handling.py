import pytest

from multi_agent_system.common.errors import MCPToolError
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
