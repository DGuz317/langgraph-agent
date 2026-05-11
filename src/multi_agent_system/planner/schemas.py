from typing import Literal

from pydantic import BaseModel, Field


AgentName = Literal["invoice", "music"]
TaskStatus = Literal["not_started", "completed", "failed"]


class PlannedTask(BaseModel):
    id: str = Field(default="")
    agent: AgentName
    intent: str
    instruction: str
    missing_fields: list[str] = Field(default_factory=list)
    status: TaskStatus = "not_started"


class PlannerOutput(BaseModel):
    status: Literal["completed"] = "completed"
    tasks: list[PlannedTask] = Field(
        default_factory=list,
        description=(
            "List of tasks to execute. Return an empty list only when the user "
            "request is unrelated to invoice or music."
        ),
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    requires_aggregation: bool = False
    missing_fields: list[str] = Field(default_factory=list)