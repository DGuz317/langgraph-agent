from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


PlannerServiceStatus = Literal["completed", "interrupted", "failed"]


class PlannerInvokeRequest(BaseModel):
    """API request for invoking or resuming the planner."""

    user_input: str = Field(min_length=1)
    thread_id: str | None = None
    resume: bool = False

    @field_validator("user_input")
    @classmethod
    def _user_input_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()

        if not cleaned:
            raise ValueError("user_input must not be blank.")

        return cleaned


class PlannerServiceResponse(BaseModel):
    """User-facing response returned by PlannerService."""

    status: PlannerServiceStatus
    thread_id: str
    final_answer: str | None = None
    interrupt_message: str | None = None
    needs_resume: bool = False
    raw_result: dict[str, Any] = Field(default_factory=dict)
