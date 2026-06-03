from multi_agent_system.a2a_servers.invoice_agent.prompts import (
    INVOICE_AGENT_SYSTEM_PROMPT,
)
from multi_agent_system.a2a_servers.invoice_agent.schemas import InvoiceAgentResponse
from multi_agent_system.common.agent_runtime import (
    AgentRuntime,
    LangChainAgentRuntime,
)


INVOICE_TOOL_NAMES = {
    "get_invoice_by_id",
    "get_invoices_by_customer_sorted_by_date",
    "get_invoice_summary_by_customer",
    "get_invoices_sorted_by_unit_price",
    "get_employee_by_invoice_and_customer",
    "get_employee_by_customer",
    "query_invoice_database",
}

INVOICE_TOOL_REQUIRED_ARGS = {
    "get_invoice_by_id": {"invoice_id"},
    "get_invoices_by_customer_sorted_by_date": {"customer_id"},
    "get_invoice_summary_by_customer": {"customer_id"},
    "get_invoices_sorted_by_unit_price": {"customer_id"},
    "get_employee_by_invoice_and_customer": {"invoice_id", "customer_id"},
    "get_employee_by_customer": {"customer_id"},
    "query_invoice_database": {"sql_query"},
}


class InvoiceAgent:
    def __init__(self, runtime: AgentRuntime | None = None) -> None:
        self._runtime = runtime or LangChainAgentRuntime(
            agent_name="invoice",
            system_prompt=INVOICE_AGENT_SYSTEM_PROMPT,
            allowed_tools=INVOICE_TOOL_NAMES,
            required_tool_args=INVOICE_TOOL_REQUIRED_ARGS,
        )

    async def ainvoke(self, query: str) -> InvoiceAgentResponse:
        try:
            result = await self._runtime.ainvoke(query)
        except Exception as exc:
            return InvoiceAgentResponse(
                success=False,
                content=f"Invoice agent failed: {exc}",
            )

        return InvoiceAgentResponse(
            success=result.success,
            content=result.content,
        )
