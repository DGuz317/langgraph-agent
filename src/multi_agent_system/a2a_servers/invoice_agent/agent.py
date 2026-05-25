import re

from multi_agent_system.a2a_servers.invoice_agent.schemas import (
    InvoiceAgentResponse,
    InvoiceIntent,
    InvoiceRequest,
)
from multi_agent_system.common.mcp_tool_agent import MCPToolAgent


class InvoiceAgent(MCPToolAgent):
    async def ainvoke(self, query: str) -> InvoiceAgentResponse:
        return await self.invoke_request(self._parse_request(query))

    async def invoke_request(self, request: InvoiceRequest) -> InvoiceAgentResponse:
        if error := self._validate_request(request):
            return error

        handlers = {
            "latest_invoice": self._get_latest_invoice,
            "all_invoices": self._get_all_invoices,
            "latest_invoice_support_employee": self._get_latest_invoice_support_employee,
            "invoices_by_unit_price": self._get_invoices_by_unit_price,
        }

        return await handlers[request.intent](request)

    def _parse_request(self, query: str) -> InvoiceRequest:
        normalized = query.lower()

        customer_id = self._extract_number(
            query,
            ["customer_id", "customer id"],
        )

        if self._is_support_employee_request(normalized):
            intent: InvoiceIntent = "latest_invoice_support_employee"
        elif "unit price" in normalized or "highest price" in normalized:
            intent: InvoiceIntent = "invoices_by_unit_price"
        elif self._is_all_invoices_request(normalized):
            intent: InvoiceIntent = "all_invoices"
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
        return await self._get_latest_invoice_with_support_employee(
            request,
            support_focused=False,
        )

    async def _get_invoices_by_unit_price(
        self,
        request: InvoiceRequest,
    ) -> InvoiceAgentResponse:
        invoices = await self.call_tool(
            "get_invoices_sorted_by_unit_price",
            {"customer_id": request.customer_id},
        )

        if not invoices:
            return InvoiceAgentResponse(
                success=True,
                content=f"No invoices found for customer_id={request.customer_id}.",
                data=[],
            )

        enriched_invoices = await self._enrich_invoices_with_support_employee(
            invoices,
            request,
        )

        return InvoiceAgentResponse(
            success=True,
            content=(
                f"Found invoices for customer_id={request.customer_id}, "
                "sorted by unit price, with support employee information."
            ),
            data=enriched_invoices,
        )

    async def _get_all_invoices(
        self,
        request: InvoiceRequest,
    ) -> InvoiceAgentResponse:
        invoices = await self.call_tool(
            "get_invoices_by_customer_sorted_by_date",
            {"customer_id": request.customer_id},
        )

        if not invoices:
            return InvoiceAgentResponse(
                success=True,
                content=f"No invoices found for customer_id={request.customer_id}.",
                data=[],
            )

        enriched_invoices = await self._enrich_invoices_with_support_employee(
            invoices,
            request,
        )

        return InvoiceAgentResponse(
            success=True,
            content=(
                f"Found {len(enriched_invoices)} invoices for "
                f"customer_id={request.customer_id} with support employee information."
            ),
            data=enriched_invoices,
        )

    async def _get_latest_invoice_support_employee(
        self,
        request: InvoiceRequest,
    ) -> InvoiceAgentResponse:
        return await self._get_latest_invoice_with_support_employee(
            request,
            support_focused=True,
        )

    async def _get_latest_invoice_with_support_employee(
        self,
        request: InvoiceRequest,
        *,
        support_focused: bool,
    ) -> InvoiceAgentResponse:
        invoices = await self.call_tool(
            "get_invoices_by_customer_sorted_by_date",
            {"customer_id": request.customer_id},
        )

        if not invoices:
            return InvoiceAgentResponse(
                success=True,
                content=f"No invoices found for customer_id={request.customer_id}.",
                data=[],
            )

        latest_invoice = invoices[0]
        invoice_id = self._extract_invoice_id(latest_invoice)

        if not invoice_id:
            return InvoiceAgentResponse(
                success=False,
                content="Latest invoice did not include an InvoiceId.",
            )

        employee = await self._get_support_employee_for_invoice(
            latest_invoice,
            request,
        )

        if isinstance(employee, dict) and employee.get("error"):
            return InvoiceAgentResponse(
                success=False,
                content=employee["error"],
                data={
                    "latest_invoice": latest_invoice,
                    "support_employee": employee,
                },
            )

        if support_focused:
            content = (
                "Support employee for latest invoice "
                f"invoice_id={invoice_id} and customer_id={request.customer_id} found."
            )
        else:
            content = (
                f"Latest invoice for customer_id={request.customer_id} found. "
                f"Support employee for invoice_id={invoice_id} included."
            )

        return InvoiceAgentResponse(
            success=True,
            content=content,
            data={
                "latest_invoice": latest_invoice,
                "support_employee": employee,
            },
        )

    def _is_support_employee_request(self, normalized: str) -> bool:
        support_terms = (
            "support employee",
            "support rep",
            "support representative",
            "employee",
        )
        return any(term in normalized for term in support_terms)

    def _is_all_invoices_request(self, normalized: str) -> bool:
        all_terms = (
            "all invoice",
            "all my invoice",
            "all invoices",
            "invoice information",
            "invoice info",
        )
        return any(term in normalized for term in all_terms)

    async def _get_support_employee_for_invoice(
        self,
        invoice: dict,
        request: InvoiceRequest,
        employee_cache: dict[str, dict] | None = None,
    ) -> dict:
        invoice_id = self._extract_invoice_id(invoice)

        if not invoice_id:
            return {
                "error": "Invoice did not include an InvoiceId."
            }

        if employee_cache is not None and invoice_id in employee_cache:
            return employee_cache[invoice_id]

        employee = await self.call_tool(
            "get_employee_by_invoice_and_customer",
            {
                "invoice_id": invoice_id,
                "customer_id": request.customer_id,
            },
        )

        if employee_cache is not None:
            employee_cache[invoice_id] = employee

        return employee

    async def _enrich_invoices_with_support_employee(
        self,
        invoices: list[dict],
        request: InvoiceRequest,
    ) -> list[dict]:
        employee_cache: dict[str, dict] = {}
        enriched_invoices = []

        for invoice in invoices:
            enriched_invoices.append(
                {
                    "invoice": invoice,
                    "support_employee": await self._get_support_employee_for_invoice(
                        invoice,
                        request,
                        employee_cache,
                    ),
                }
            )

        return enriched_invoices

    def _extract_invoice_id(self, invoice: dict) -> str:
        return str(invoice.get("InvoiceId", "")).strip()

    def _extract_number(self, text: str, field_names: list[str]) -> str | None:
        normalized = text.lower()

        for field_name in field_names:
            pattern = rf"\b{re.escape(field_name)}\b\s*(?:=|:|is)?\s*(\d+)"
            match = re.search(pattern, normalized)

            if match:
                return match.group(1)

        return None
