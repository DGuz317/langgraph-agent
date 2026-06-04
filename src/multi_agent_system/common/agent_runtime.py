from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol
from uuid import uuid4

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest

from multi_agent_system.common.execution_evidence import (
    EvidenceAgent,
    ExecutionEvidence,
    record_execution_evidence,
)
from multi_agent_system.common.llm import get_llm
from multi_agent_system.common.observability import trace_config
from multi_agent_system.common.runnable import ainvoke_with_optional_config
from multi_agent_system.config import settings


@dataclass
class AgentRunResult:
    success: bool
    content: str
    messages: list[Any] = field(default_factory=list)


class AgentRuntime(Protocol):
    async def ainvoke(self, instruction: str) -> AgentRunResult:
        """Run an agent against one natural-language instruction."""


class LangChainAgentRuntime:
    """LangChain tool-calling runtime backed by MCP tools."""

    def __init__(
        self,
        *,
        agent_name: EvidenceAgent,
        system_prompt: str,
        allowed_tools: set[str] | None = None,
        required_tool_args: Mapping[str, set[str]] | None = None,
    ) -> None:
        self._agent_name = agent_name
        self._system_prompt = system_prompt
        self._allowed_tools = allowed_tools
        self._required_tool_args = {
            tool_name: set(required_args)
            for tool_name, required_args in (required_tool_args or {}).items()
        }
        self._agent: Any | None = None

    async def ainvoke(self, instruction: str) -> AgentRunResult:
        agent = await self._get_agent()
        result = await ainvoke_with_optional_config(
            agent,
            {"messages": [{"role": "user", "content": instruction}]},
            config=trace_config(
                run_name=f"{self._agent_name}.agent",
                tags=[self._agent_name, "agent"],
            ),
        )
        messages = _result_messages(result)
        return AgentRunResult(
            success=True,
            content=_last_assistant_text(messages) or "Agent completed without text.",
            messages=messages,
        )

    async def _get_agent(self) -> Any:
        if self._agent is not None:
            return self._agent

        client = MultiServerMCPClient(
            {
                "default": {
                    "transport": "streamable_http",
                    "url": settings.mcp_server_url,
                }
            },
            tool_interceptors=[self._record_tool_evidence],
        )
        tools = await client.get_tools()
        if self._allowed_tools is not None:
            tools = [
                tool
                for tool in tools
                if str(getattr(tool, "name", "")) in self._allowed_tools
            ]

        self._agent = create_agent(
            model=get_llm(),
            tools=tools,
            system_prompt=self._system_prompt,
        )
        return self._agent

    async def _record_tool_evidence(
        self,
        request: MCPToolCallRequest,
        handler,
    ):
        call_id = str(uuid4())
        request = _normalize_tool_request(
            request,
            required_args=self._required_tool_args.get(request.name, set()),
        )
        record_execution_evidence(
            ExecutionEvidence(
                kind="mcp_tool_call",
                agent=self._agent_name,
                operation=request.name,
                status="started",
                call_id=call_id,
                fields=sorted(str(key) for key in request.args),
                arguments=dict(request.args),
                summary=f"Called {request.name}.",
            )
        )

        missing_args = _missing_required_args(
            request.args,
            self._required_tool_args.get(request.name, set()),
        )
        if missing_args:
            record_execution_evidence(
                ExecutionEvidence(
                    kind="mcp_tool_result",
                    agent=self._agent_name,
                    operation=request.name,
                    status="failed",
                    call_id=call_id,
                    summary=(
                        f"{request.name} was not called because required "
                        f"argument(s) were missing: {', '.join(missing_args)}."
                    ),
                )
            )
            raise ValueError(
                f"Tool {request.name} requires non-empty argument(s): "
                f"{', '.join(missing_args)}."
            )

        try:
            result = await handler(request)
        except Exception:
            record_execution_evidence(
                ExecutionEvidence(
                    kind="mcp_tool_result",
                    agent=self._agent_name,
                    operation=request.name,
                    status="failed",
                    call_id=call_id,
                    summary=f"{request.name} failed.",
                )
            )
            raise

        record_execution_evidence(
            ExecutionEvidence(
                kind="mcp_tool_result",
                agent=self._agent_name,
                operation=request.name,
                status="completed",
                call_id=call_id,
                summary=_summarize_tool_result(request.name, result),
            )
        )
        return result


def _result_messages(result: Any) -> list[Any]:
    if isinstance(result, dict):
        messages = result.get("messages", [])
        if isinstance(messages, list):
            return messages
    return []


def _last_assistant_text(messages: list[Any]) -> str:
    for message in reversed(messages):
        message_type = getattr(message, "type", None)
        role = getattr(message, "role", None)
        if message_type not in {"ai", "assistant"} and role != "assistant":
            continue

        text = _content_text(getattr(message, "content", ""))
        if text:
            return text

    return ""


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(part.strip() for part in parts if part.strip())

    return str(content).strip() if content is not None else ""


def _normalize_tool_request(
    request: MCPToolCallRequest,
    *,
    required_args: set[str],
) -> MCPToolCallRequest:
    if not required_args:
        return request

    normalized_args = dict(request.args)
    changed = False

    for arg_name in required_args:
        value = normalized_args.get(arg_name)
        if value is None or isinstance(value, str):
            continue

        normalized_args[arg_name] = str(value)
        changed = True

    if not changed:
        return request

    return MCPToolCallRequest(
        name=request.name,
        args=normalized_args,
        server_name=request.server_name,
        headers=request.headers,
        runtime=request.runtime,
    )


def _missing_required_args(args: dict[str, Any], required_args: set[str]) -> list[str]:
    missing: list[str] = []

    for arg_name in sorted(required_args):
        if arg_name not in args:
            missing.append(arg_name)
            continue

        value = args[arg_name]
        if value is None:
            missing.append(arg_name)
        elif isinstance(value, str) and not value.strip():
            missing.append(arg_name)

    return missing


def _summarize_tool_result(tool_name: str, result: Any) -> str:
    structured = _structured_result(result)
    if structured is None:
        return f"{tool_name} completed."

    if isinstance(structured, list):
        preview = _preview_json(structured[:3])
        suffix = f" Preview: {preview}" if preview else ""
        return f"{tool_name} completed; {len(structured)} record(s) returned.{suffix}"

    preview = _preview_json(structured)
    if preview:
        return f"{tool_name} completed. Outcome: {preview}"

    return f"{tool_name} completed."


def _structured_result(result: Any) -> Any:
    structured = getattr(result, "structuredContent", None)
    if structured is not None:
        if isinstance(structured, dict) and "result" in structured:
            return structured["result"]
        return structured

    content = getattr(result, "content", None)
    if not content:
        return None

    if isinstance(content, list) and len(content) == 1:
        text = getattr(content[0], "text", None)
        if isinstance(text, str):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text

    return content


def _preview_json(value: Any, *, max_chars: int = 900) -> str:
    try:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    except TypeError:
        text = str(value)

    if len(text) <= max_chars:
        return text

    return f"{text[: max_chars - 3]}..."
