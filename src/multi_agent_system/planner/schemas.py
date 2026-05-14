from typing import Literal

from pydantic import BaseModel, Field


AgentName = Literal["invoice", "music"]
TaskStatus = Literal["not_started", "completed", "failed"]


class PlannedTask(BaseModel):
    id: str
    agent: AgentName
    intent: str
    instruction: str
    args: dict[str, str] = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)
    status: TaskStatus = "not_started"


class PlannerOutput(BaseModel):
    status: Literal["completed", "failed"]
    tasks: list[PlannedTask] = Field(default_factory=list)
    confidence: float
    requires_aggregation: bool
    missing_fields: list[str] = Field(default_factory=list)