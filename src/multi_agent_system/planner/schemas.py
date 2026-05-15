from typing import Literal

from pydantic import BaseModel, Field


AgentName = Literal["invoice", "music"]
TaskStatus = Literal["not_started", "completed", "failed"]
TaskIntent = Literal[
    "latest_invoice",
    "invoices_by_unit_price",
    "tracks_by_artist",
    "albums_by_artist",
    "songs_by_genre",
    "check_song",
    "clarify_music_search",
]


class PlannedTask(BaseModel):
    id: str = Field(
        description="Unique task id. Use an empty string if not available.",
    )
    agent: AgentName = Field(
        description="Target specialized agent. Must be invoice or music.",
    )
    intent: TaskIntent = Field(
        description="The exact intent the target agent should execute.",
    )
    instruction: str = Field(
        description="Executable natural-language instruction for the target agent.",
    )
    args: dict[str, str] = Field(
        default_factory=dict,
        description="Structured extracted arguments for the task.",
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        description="Fields still missing before this task can run.",
    )
    status: TaskStatus = Field(
        default="not_started",
        description="Task execution status.",
    )


class PlannerOutput(BaseModel):
    status: Literal["completed", "failed"] = Field(
        description="Planner status.",
    )
    tasks: list[PlannedTask] = Field(
        description=(
            "Planned tasks. Must contain at least one task for invoice or music requests. "
            "Use an empty list only for requests unrelated to invoice or music."
        ),
    )
    confidence: float = Field(
        description="Planner confidence from 0.0 to 1.0.",
    )
    requires_aggregation: bool = Field(
        description="True when more than one agent/task result must be combined.",
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        description="Top-level missing fields aggregated from all tasks.",
    )