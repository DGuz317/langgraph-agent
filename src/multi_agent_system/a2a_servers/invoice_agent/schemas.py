from typing import Literal

from pydantic import BaseModel, Field

from multi_agent_system.common.execution_evidence import ExecutionEvidence

# TODO: This
InvoiceIntent = Literal[
    "invoice_query",
    "latest_invoice",
    "invoice_detail",
    "invoice_summary",
    "customer_support_employee",
    "all_invoices",
    "latest_invoice_support_employee",
    "invoices_by_unit_price",
]


class InvoiceRequest(BaseModel):
    intent: InvoiceIntent
    customer_id: str | None = None
    invoice_id: str | None = None
    limit: str | None = None
    sort_by: str | None = None
    sort_order: str | None = None
    include_support_employee: str | None = "true"


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
            limit=self.args.get("limit"),
            sort_by=self.args.get("sort_by"),
            sort_order=self.args.get("sort_order"),
            include_support_employee=self.args.get(
                "include_support_employee",
                "true",
            ),
        )


class InvoiceAgentResponse(BaseModel):
    success: bool
    content: str
    data: list[dict] | dict | None = None
    execution_evidence: list[ExecutionEvidence] = Field(default_factory=list)
