from typing import Any, Literal

from pydantic import BaseModel, Field


PlannerServiceStatus = Literal["completed", "interrupted", "failed"]


class PlannerServiceResponse(BaseModel):
    """User-facing response returned by PlannerService."""

    status: PlannerServiceStatus
    thread_id: str
    final_answer: str | None = None
    interrupt_message: str | None = None
    needs_resume: bool = False
    raw_result: dict[str, Any] = Field(default_factory=dict)