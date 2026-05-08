import json
import re
from typing import Any, Literal

from langchain_mcp_adapters.client import MultiServerMCPClient
from pydantic import BaseModel

from multi_agent_system.config import settings
from multi_agent_system.a2a_servers.invoice_agent.schemas import (
    InvoiceAgentResponse,
)


InvoiceIntent = Literal[
    "latest_invoice",
    "invoices_by_unit_price",
    "support_employee",
]


class InvoiceRequest(BaseModel):
    intent: InvoiceIntent
    customer_id: str | None = None
    invoice_id: str | None = None


class InvoiceAgent:
    def __init__(self) -> None:
        self.mcp_client = MultiServerMCPClient(
            {
                "multi_agent_mcp": {
                    "transport": "streamable_http",
                    "url": settings.mcp_server_url,
                }
            }
        )

    async def ainvoke(self, query: str) -> InvoiceAgentResponse:
        request = self._parse_request(query)

        if error := self._validate_request(request):
            return error

        if request.intent == "support_employee":
            return await self._get_support_employee(request)

        if request.intent == "invoices_by_unit_price":
            return await self._get_invoices_by_unit_price(request)

        return await self._get_latest_invoice(request)

    def _parse_request(self, query: str) -> InvoiceRequest:
        normalized = query.lower()

        customer_id = self._extract_number(query, ["customer_id", "customer id", "id"])
        invoice_id = self._extract_number(query, ["invoice_id", "invoice id"])

        if "employee" in normalized or "support rep" in normalized:
            intent: InvoiceIntent = "support_employee"
        elif "unit price" in normalized or "highest price" in normalized:
            intent = "invoices_by_unit_price"
        else:
            intent = "latest_invoice"

        return InvoiceRequest(
            intent=intent,
            customer_id=customer_id,
            invoice_id=invoice_id,
        )

    def _validate_request(
        self,
        request: InvoiceRequest,
    ) -> InvoiceAgentResponse | None:
        if not request.customer_id:
            return InvoiceAgentResponse(
                success=False,
                content="Missing required field: customer_id.",
            )

        if request.intent == "support_employee" and not request.invoice_id:
            return InvoiceAgentResponse(
                success=False,
                content="Missing required field: invoice_id.",
            )

        return None

    async def _get_latest_invoice(
        self,
        request: InvoiceRequest,
    ) -> InvoiceAgentResponse:
        data = await self._call_tool(
            "get_invoices_by_customer_sorted_by_date",
            {"customer_id": request.customer_id},
        )

        if not data:
            return InvoiceAgentResponse(
                success=True,
                content=f"No invoices found for customer_id={request.customer_id}.",
                data=[],
            )

        return InvoiceAgentResponse(
            success=True,
            content=f"Latest invoice for customer_id={request.customer_id} found.",
            data=data[0],
        )

    async def _get_invoices_by_unit_price(
        self,
        request: InvoiceRequest,
    ) -> InvoiceAgentResponse:
        data = await self._call_tool(
            "get_invoices_sorted_by_unit_price",
            {"customer_id": request.customer_id},
        )

        return InvoiceAgentResponse(
            success=True,
            content=(
                f"Found invoices for customer_id={request.customer_id}, "
                "sorted by unit price."
            ),
            data=data,
        )

    async def _get_support_employee(
        self,
        request: InvoiceRequest,
    ) -> InvoiceAgentResponse:
        data = await self._call_tool(
            "get_employee_by_invoice_and_customer",
            {
                "customer_id": request.customer_id,
                "invoice_id": request.invoice_id,
            },
        )

        return InvoiceAgentResponse(
            success=True,
            content=f"Found support employee for invoice_id={request.invoice_id}.",
            data=data,
        )

    async def _call_tool(self, tool_name: str, args: dict[str, Any]) -> Any:
        tools = await self.mcp_client.get_tools()
        tool_map = {tool.name: tool for tool in tools}

        if tool_name not in tool_map:
            raise RuntimeError(
                f"MCP tool not found: {tool_name}. "
                f"Available tools: {list(tool_map.keys())}"
            )

        result = await tool_map[tool_name].ainvoke(args)
        return self._unwrap_mcp_result(result)

    def _extract_number(self, text: str, field_names: list[str]) -> str | None:
        normalized = text.lower()

        for field_name in field_names:
            pattern = rf"{re.escape(field_name)}\s*(?:=|:|is)?\s*(\d+)"
            match = re.search(pattern, normalized)

            if match:
                return match.group(1)

        return None

    def _unwrap_mcp_result(self, result: Any) -> Any:
        if isinstance(result, dict) and result.get("type") == "text":
            text = result.get("text", "")

            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text

        return result