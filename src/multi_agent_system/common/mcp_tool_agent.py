import json
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient

from multi_agent_system.config import settings


class MCPToolAgent:
    def __init__(self) -> None:
        self.mcp_client = MultiServerMCPClient(
            {
                "multi_agent_mcp": {
                    "transport": "streamable_http",
                    "url": settings.mcp_server_url,
                }
            }
        )

    async def call_tool(self, tool_name: str, args: dict[str, Any]) -> Any:
        tools = await self.mcp_client.get_tools()
        tool_map = {tool.name: tool for tool in tools}

        if tool_name not in tool_map:
            raise RuntimeError(
                f"MCP tool not found: {tool_name}. "
                f"Available tools: {list(tool_map.keys())}"
            )

        result = await tool_map[tool_name].ainvoke(args)
        return self._unwrap_mcp_result(result)

    def _unwrap_mcp_result(self, result: Any) -> Any:
        if isinstance(result, dict) and result.get("type") == "text":
            text = result.get("text", "")

            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text

        return result