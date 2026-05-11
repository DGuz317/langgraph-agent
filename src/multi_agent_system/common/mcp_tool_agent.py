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
        if isinstance(result, list) and len(result) == 1:
            first_item = result[0]

            if isinstance(first_item, dict) and first_item.get("type") == "text":
                return self._parse_text_result(first_item.get("text", ""))

        if isinstance(result, dict) and result.get("type") == "text":
            return self._parse_text_result(result.get("text", ""))

        return result


    def _parse_text_result(self, text: str) -> Any:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text