from pydantic import BaseModel


class InvoiceAgentResponse(BaseModel):
    success: bool
    content: str
    data: list[dict] | dict | None = None