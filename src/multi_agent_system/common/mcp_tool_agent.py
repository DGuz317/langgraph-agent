import json
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient

from multi_agent_system.common.errors import MCPToolError
from multi_agent_system.config import settings


class MCPToolAgent:
    """Base class for agents that call tools exposed by the MCP server."""

    def __init__(self, client: MultiServerMCPClient | None = None) -> None:
        self._client = client

    def _build_client(self) -> MultiServerMCPClient:
        return MultiServerMCPClient(
            {
                "default": {
                    "transport": "streamable_http",
                    "url": settings.mcp_server_url,
                }
            }
        )

    async def get_tools(self) -> list[Any]:
        client = self._client or self._build_client()

        try:
            tools = await client.get_tools()
        except Exception as exc:
            raise MCPToolError(f"Failed to load MCP tools: {exc}") from exc

        return list(tools)

    async def call_tool(
        self,
        tool_name: str,
        args: dict[str, Any],
    ) -> Any:
        tool = await self._find_tool(tool_name)

        try:
            raw_result = await tool.ainvoke(args)
        except Exception as exc:
            raise MCPToolError(
                f"MCP tool '{tool_name}' invocation failed: {exc}"
            ) from exc

        return self._unwrap_mcp_result(raw_result, tool_name=tool_name)

    async def _find_tool(self, tool_name: str) -> Any:
        tools = await self.get_tools()

        for tool in tools:
            if getattr(tool, "name", None) == tool_name:
                return tool

        available = ", ".join(
            sorted(
                str(getattr(tool, "name", "<unnamed>"))
                for tool in tools
            )
        )

        if not available:
            available = "none"

        raise MCPToolError(
            f"MCP tool '{tool_name}' was not found. Available tools: {available}."
        )

    def _unwrap_mcp_result(
        self,
        raw_result: Any,
        *,
        tool_name: str,
    ) -> Any:
        if raw_result is None:
            return None

        if isinstance(raw_result, str):
            return self._parse_json_text(raw_result, tool_name=tool_name)

        if isinstance(raw_result, dict):
            return self._unwrap_dict_result(raw_result, tool_name=tool_name)

        if isinstance(raw_result, list):
            return self._unwrap_list_result(raw_result, tool_name=tool_name)

        raise MCPToolError(
            f"MCP tool '{tool_name}' returned unsupported result type: "
            f"{type(raw_result).__name__}."
        )

    def _unwrap_dict_result(
        self,
        result: dict[str, Any],
        *,
        tool_name: str,
    ) -> Any:
        if "text" in result:
            text = result["text"]

            if not isinstance(text, str):
                raise MCPToolError(
                    f"MCP tool '{tool_name}' returned non-string text payload."
                )

            return self._parse_json_text(text, tool_name=tool_name)

        if "content" in result:
            return self._unwrap_mcp_result(result["content"], tool_name=tool_name)

        if "structuredContent" in result:
            return result["structuredContent"]

        return result

    def _unwrap_list_result(
        self,
        result: list[Any],
        *,
        tool_name: str,
    ) -> Any:
        if not result:
            return []

        if all(isinstance(item, dict) and "text" in item for item in result):
            parsed_items = [
                self._unwrap_dict_result(item, tool_name=tool_name)
                for item in result
            ]

            if len(parsed_items) == 1:
                return parsed_items[0]

            return parsed_items

        if len(result) == 1 and isinstance(result[0], dict):
            return self._unwrap_dict_result(result[0], tool_name=tool_name)

        return result

    def _parse_json_text(
        self,
        text: str,
        *,
        tool_name: str,
    ) -> Any:
        cleaned = text.strip()

        if not cleaned:
            return ""

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise MCPToolError(
                f"MCP tool '{tool_name}' returned invalid JSON text."
            ) from exc
