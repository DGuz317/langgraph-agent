from multi_agent_system.a2a_client.base import BaseA2AClient
from multi_agent_system.config import settings


class InvoiceA2AClient(BaseA2AClient):
    def __init__(self) -> None:
        super().__init__(
            url=f"{settings.invoice_a2a_url.rstrip('/')}/a2a/jsonrpc/",
            timeout_seconds=settings.a2a_timeout_seconds,
        )

    async def get_latest_invoice(self, customer_id: str) -> str:
        return await self.ask(f"Get latest invoice for customer_id={customer_id}")

    async def get_invoices_by_unit_price(self, customer_id: str) -> str:
        return await self.ask(
            f"Show invoices for customer_id={customer_id} sorted by unit price"
        )

    async def get_support_employee(self, customer_id: str, invoice_id: str) -> str:
        return await self.ask(
            f"Find employee for invoice_id={invoice_id} and customer_id={customer_id}"
        )