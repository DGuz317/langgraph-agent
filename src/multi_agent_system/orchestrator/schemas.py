from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


PlannerServiceStatus = Literal["completed", "interrupted", "failed"]


class PlannerInvokeRequest(BaseModel):
    """API request for invoking or resuming the planner."""

    user_input: str = Field(min_length=1)
    thread_id: str | None = None
    resume: bool | None = None

    @field_validator("user_input")
    @classmethod
    def _user_input_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()

        if not cleaned:
            raise ValueError("user_input must not be blank.")

        return cleaned

    @field_validator("thread_id")
    @classmethod
    def _thread_id_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None

        cleaned = value.strip()
        if not cleaned:
            raise ValueError("thread_id must not be blank.")

        return cleaned

    @model_validator(mode="after")
    def _resume_requires_thread_id(self) -> "PlannerInvokeRequest":
        if self.resume is True and not self.thread_id:
            raise ValueError("resume=true requires thread_id.")
        return self


class PlannerServiceResponse(BaseModel):
    """User-facing response returned by PlannerService."""

    status: PlannerServiceStatus
    thread_id: str
    final_answer: str | None = None
    interrupt_message: str | None = None
    needs_resume: bool = False
    raw_result: dict[str, Any] = Field(default_factory=dict)
