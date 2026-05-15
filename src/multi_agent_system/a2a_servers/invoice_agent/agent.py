import re
from typing import Literal

from pydantic import BaseModel

from multi_agent_system.a2a_servers.invoice_agent.schemas import (
    InvoiceAgentResponse,
)
from multi_agent_system.common.mcp_tool_agent import MCPToolAgent


InvoiceIntent = Literal[
    "latest_invoice",
    "invoices_by_unit_price",
]


class InvoiceRequest(BaseModel):
    intent: InvoiceIntent
    customer_id: str | None = None


class InvoiceAgent(MCPToolAgent):
    async def ainvoke(self, query: str) -> InvoiceAgentResponse:
        request = self._parse_request(query)

        if error := self._validate_request(request):
            return error

        handlers = {
            "latest_invoice": self._get_latest_invoice,
            "invoices_by_unit_price": self._get_invoices_by_unit_price,
        }

        return await handlers[request.intent](request)

    def _parse_request(self, query: str) -> InvoiceRequest:
        normalized = query.lower()

        customer_id = self._extract_number(
            query,
            ["customer_id", "customer id"],
        )

        if "unit price" in normalized or "highest price" in normalized:
            intent: InvoiceIntent = "invoices_by_unit_price"
        else:
            intent = "latest_invoice"

        return InvoiceRequest(
            intent=intent,
            customer_id=customer_id,
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

        return None

    async def _get_latest_invoice(
        self,
        request: InvoiceRequest,
    ) -> InvoiceAgentResponse:
        data = await self.call_tool(
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
        data = await self.call_tool(
            "get_invoices_sorted_by_unit_price",
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
            content=(
                f"Found invoices for customer_id={request.customer_id}, "
                "sorted by unit price."
            ),
            data=data,
        )

    def _extract_number(self, text: str, field_names: list[str]) -> str | None:
        normalized = text.lower()

        for field_name in field_names:
            pattern = rf"\b{re.escape(field_name)}\b\s*(?:=|:|is)?\s*(\d+)"
            match = re.search(pattern, normalized)

            if match:
                return match.group(1)

        return None