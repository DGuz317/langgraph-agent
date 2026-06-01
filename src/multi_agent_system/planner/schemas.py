from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


AgentName = Literal["invoice", "music"]
TaskStatus = Literal["not_started", "completed", "failed"]


class PlannedTask(BaseModel):
    id: str = Field(
        default="",
        description="Unique task id. Use an empty string if not available.",
    )
    agent: AgentName = Field(
        description="Target specialized agent. Must be invoice or music.",
    )
    instruction: str = Field(
        description=(
            "Natural-language instruction for the target agent. Include all known "
            "user constraints so the target agent can choose tools and arguments."
        ),
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        description="Fields still missing before this task can run.",
    )
    status: TaskStatus = Field(
        default="not_started",
        description="Task execution status.",
    )

    @field_validator("instruction")
    @classmethod
    def _instruction_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("instruction must not be blank.")
        return cleaned

    @field_validator("missing_fields", mode="before")
    @classmethod
    def _normalize_missing_fields(cls, value: Any) -> list[str]:
        if value is None:
            return []

        if not isinstance(value, list):
            raise TypeError("missing_fields must be a list.")

        return [
            str(item).strip()
            for item in value
            if item is not None and str(item).strip()
        ]


class PlannerOutput(BaseModel):
    status: Literal["completed", "failed"] = Field(
        description="Planner status.",
    )
    tasks: list[PlannedTask] = Field(
        description=(
            "Dispatch tasks. Use an empty list only for requests unrelated to "
            "available agents."
        ),
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Planner confidence from 0.0 to 1.0.",
    )
    requires_aggregation: bool = Field(
        description="True when more than one agent/task result must be combined.",
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        description="Top-level missing fields aggregated from all tasks.",
    )

    @field_validator("missing_fields", mode="before")
    @classmethod
    def _normalize_missing_fields(cls, value: Any) -> list[str]:
        if value is None:
            return []

        if not isinstance(value, list):
            raise TypeError("missing_fields must be a list.")

        return [
            str(item).strip()
            for item in value
            if item is not None and str(item).strip()
        ]

    @model_validator(mode="after")
    def _validate_output_consistency(self) -> PlannerOutput:
        if len(self.tasks) > 1 and not self.requires_aggregation:
            raise ValueError(
                "requires_aggregation must be true when planner returns multiple tasks."
            )
        return self
