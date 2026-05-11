from typing import Literal

from pydantic import BaseModel, Field


AgentName = Literal["invoice", "music"]
TaskStatus = Literal["not_started", "completed", "failed"]


class PlannedTask(BaseModel):
    id: str
    agent: AgentName
    instruction: str
    required_fields: list[str] = Field(default_factory=list)
    status: TaskStatus = "not_started"


class PlannerOutput(BaseModel):
    status: Literal["completed"] = "completed"
    answer: list[PlannedTask]
    confidence: float = 1.0
    requires_aggregation: bool = False
    missing_fields: list[str] = Field(default_factory=list)