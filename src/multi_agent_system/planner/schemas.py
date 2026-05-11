from typing import Literal

from pydantic import BaseModel, Field


AgentName = Literal["invoice", "music"]
TaskStatus = Literal["not_started", "completed", "failed"]


class PlannedTask(BaseModel):
    id: str = Field(
        default="",
        description="Unique task id. Leave empty if unknown; the system will fill it.",
    )
    agent: AgentName = Field(
        description="Target agent. Must be either invoice or music.",
    )
    intent: str = Field(
        description=(
            "Intent name. Use one of: latest_invoice, invoices_by_unit_price, "
            "support_employee, tracks_by_artist, albums_by_artist, "
            "songs_by_genre, check_song."
        ),
    )
    instruction: str = Field(
        description=(
            "Clear executable instruction for the target agent. "
            "Include known customer_id, invoice_id, artist, genre, or song_title."
        ),
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        description=(
            "Only fields missing from the user's message. "
            "Do not include fields already provided by the user."
        ),
    )
    status: TaskStatus = "not_started"


class PlannerOutput(BaseModel):
    status: Literal["completed"] = "completed"
    answer: list[PlannedTask] = Field(
        default_factory=list,
        description=(
            "Tasks to execute. Return an empty list only if the request is unrelated "
            "to invoice and music."
        ),
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    requires_aggregation: bool = Field(
        default=False,
        description="True only when there is more than one task.",
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        description="Unique list of missing fields across all tasks.",
    )