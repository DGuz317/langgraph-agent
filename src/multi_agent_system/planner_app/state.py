from typing import Any, TypedDict


class PlannerAppState(TypedDict, total=False):
    user_input: str
    resume_input: str | None

    planner_output: dict[str, Any]
    missing_fields: list[str]

    customer_id: str | None
    artist: str | None
    genre: str | None

    invoice_result: str | None
    music_result: str | None

    final_answer: str | None