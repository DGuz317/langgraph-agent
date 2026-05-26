from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


AgentName = Literal["invoice", "music"]
TaskStatus = Literal["not_started", "completed", "failed"]
TaskIntent = Literal[
    "latest_invoice",
    "invoice_detail",
    "invoice_summary",
    "customer_support_employee",
    "all_invoices",
    "latest_invoice_support_employee",
    "invoices_by_unit_price",
    "tracks_by_artist",
    "albums_by_artist",
    "songs_by_genre",
    "check_song",
    "clarify_music_search",
]


INVOICE_INTENTS = {
    "latest_invoice",
    "invoice_detail",
    "invoice_summary",
    "customer_support_employee",
    "all_invoices",
    "latest_invoice_support_employee",
    "invoices_by_unit_price",
}

MUSIC_INTENTS = {
    "tracks_by_artist",
    "albums_by_artist",
    "songs_by_genre",
    "check_song",
    "clarify_music_search",
}

REQUIRED_ARGS_BY_INTENT = {
    "latest_invoice": "customer_id",
    "invoice_detail": "invoice_id",
    "invoice_summary": "customer_id",
    "customer_support_employee": "customer_id",
    "all_invoices": "customer_id",
    "latest_invoice_support_employee": "customer_id",
    "invoices_by_unit_price": "customer_id",
    "tracks_by_artist": "artist",
    "albums_by_artist": "artist",
    "songs_by_genre": "genre",
    "check_song": "song_title",
}

CLARIFY_MUSIC_FIELD = "music_search_type"


class PlannedTask(BaseModel):
    id: str = Field(
        default="",
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

    @field_validator("instruction")
    @classmethod
    def _instruction_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()

        if not cleaned:
            raise ValueError("instruction must not be blank.")

        return cleaned

    @field_validator("args", mode="before")
    @classmethod
    def _normalize_args(cls, value: Any) -> dict[str, str]:
        if value is None:
            return {}

        if not isinstance(value, dict):
            raise TypeError("args must be a dictionary.")

        normalized: dict[str, str] = {}

        for key, item in value.items():
            if item is None:
                continue

            normalized[str(key)] = str(item).strip()

        return normalized

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
            if str(item).strip()
        ]

    @model_validator(mode="after")
    def _validate_agent_intent_and_required_fields(self) -> PlannedTask:
        if self.agent == "invoice" and self.intent not in INVOICE_INTENTS:
            raise ValueError(
                f"Intent '{self.intent}' is not valid for invoice agent."
            )

        if self.agent == "music" and self.intent not in MUSIC_INTENTS:
            raise ValueError(
                f"Intent '{self.intent}' is not valid for music agent."
            )

        if self.intent == "clarify_music_search":
            if CLARIFY_MUSIC_FIELD not in self.missing_fields:
                raise ValueError(
                    "clarify_music_search requires "
                    f"missing_fields=['{CLARIFY_MUSIC_FIELD}']."
                )

            return self

        required_arg = REQUIRED_ARGS_BY_INTENT.get(self.intent)

        if required_arg is None:
            return self

        if _has_arg_value(self.args, required_arg):
            return self

        if required_arg in self.missing_fields:
            return self

        raise ValueError(
            f"Intent '{self.intent}' requires arg '{required_arg}' "
            f"or missing_fields entry '{required_arg}'."
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
            if str(item).strip()
        ]

    @model_validator(mode="after")
    def _validate_output_consistency(self) -> PlannerOutput:
        if len(self.tasks) > 1 and not self.requires_aggregation:
            raise ValueError(
                "requires_aggregation must be true when planner returns multiple tasks."
            )

        return self


def _has_arg_value(args: dict[str, str], key: str) -> bool:
    value = args.get(key)

    if value is None:
        return False

    return bool(str(value).strip())
