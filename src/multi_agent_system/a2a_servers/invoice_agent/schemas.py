from typing import Literal

from pydantic import BaseModel, Field


InvoiceIntent = Literal[
    "latest_invoice",
    "invoice_detail",
    "all_invoices",
    "latest_invoice_support_employee",
    "invoices_by_unit_price",
]


class InvoiceRequest(BaseModel):
    intent: InvoiceIntent
    customer_id: str | None = None
    invoice_id: str | None = None


class InvoiceTaskPayload(BaseModel):
    agent: Literal["invoice"]
    intent: InvoiceIntent
    args: dict[str, str] = Field(default_factory=dict)
    instruction: str | None = None

    def to_request(self) -> InvoiceRequest:
        return InvoiceRequest(
            intent=self.intent,
            customer_id=self.args.get("customer_id"),
            invoice_id=self.args.get("invoice_id"),
        )


class InvoiceAgentResponse(BaseModel):
    success: bool
    content: str
    data: list[dict] | dict | None = None
