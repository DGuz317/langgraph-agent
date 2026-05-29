import pytest
from pydantic import ValidationError

from multi_agent_system.planner.schemas import PlannedTask, PlannerOutput


def test_planned_task_accepts_complete_invoice_task() -> None:
    task = PlannedTask(
        id="task-1",
        agent="invoice",
        intent="latest_invoice",
        instruction="Get latest invoice for customer_id=5",
        args={"customer_id": "5"},
        missing_fields=[],
    )

    assert task.args == {"customer_id": "5"}


def test_planned_task_accepts_latest_invoice_support_employee_task() -> None:
    task = PlannedTask(
        id="task-1",
        agent="invoice",
        intent="latest_invoice_support_employee",
        instruction="Get support employee for latest invoice for customer_id=5",
        args={"customer_id": "5"},
        missing_fields=[],
    )

    assert task.args == {"customer_id": "5"}


def test_planned_task_accepts_invoice_detail_task() -> None:
    task = PlannedTask(
        id="task-1",
        agent="invoice",
        intent="invoice_detail",
        instruction="Get invoice detail for invoice_id=361",
        args={"invoice_id": "361"},
        missing_fields=[],
    )

    assert task.args == {"invoice_id": "361"}


def test_planned_task_accepts_invoice_query_and_enforces_support_employee() -> None:
    task = PlannedTask(
        id="task-1",
        agent="invoice",
        intent="invoice_query",
        instruction="Get 5 most recent invoices for customer_id=8 with support employee",
        args={
            "customer_id": "8",
            "limit": 5,
            "sort_by": "invoice_date",
            "sort_order": "desc",
        },
        missing_fields=[],
    )

    assert task.args == {
        "customer_id": "8",
        "limit": "5",
        "sort_by": "invoice_date",
        "sort_order": "desc",
        "include_support_employee": "true",
    }


def test_planned_task_rejects_invoice_query_without_identifier() -> None:
    with pytest.raises(ValidationError, match="invoice_id or customer_id"):
        PlannedTask(
            id="task-1",
            agent="invoice",
            intent="invoice_query",
            instruction="Get invoices",
            args={"include_support_employee": "true"},
            missing_fields=[],
        )


def test_planned_task_allows_missing_invoice_id_when_declared() -> None:
    task = PlannedTask(
        id="task-1",
        agent="invoice",
        intent="invoice_detail",
        instruction="Ask for invoice_id",
        args={},
        missing_fields=["invoice_id"],
    )

    assert task.missing_fields == ["invoice_id"]


def test_planned_task_accepts_invoice_summary_task() -> None:
    task = PlannedTask(
        id="task-1",
        agent="invoice",
        intent="invoice_summary",
        instruction="Get invoice summary for customer_id=5",
        args={"customer_id": "5"},
        missing_fields=[],
    )

    assert task.args == {"customer_id": "5"}


def test_planned_task_accepts_customer_support_employee_task() -> None:
    task = PlannedTask(
        id="task-1",
        agent="invoice",
        intent="customer_support_employee",
        instruction="Get support employee for customer_id=5",
        args={"customer_id": "5"},
        missing_fields=[],
    )

    assert task.args == {"customer_id": "5"}


def test_planned_task_accepts_all_invoices_task() -> None:
    task = PlannedTask(
        id="task-1",
        agent="invoice",
        intent="all_invoices",
        instruction="Get all invoices for customer_id=5",
        args={"customer_id": "5"},
        missing_fields=[],
    )

    assert task.args == {"customer_id": "5"}


def test_planned_task_normalizes_arg_values_to_strings() -> None:
    task = PlannedTask(
        id="task-1",
        agent="invoice",
        intent="latest_invoice",
        instruction="Get latest invoice for customer_id=5",
        args={"customer_id": 5},
        missing_fields=[],
    )

    assert task.args == {"customer_id": "5"}


def test_planned_task_allows_missing_required_arg_when_missing_field_is_declared() -> None:
    task = PlannedTask(
        id="task-1",
        agent="invoice",
        intent="latest_invoice",
        instruction="Ask for customer_id",
        args={},
        missing_fields=["customer_id"],
    )

    assert task.missing_fields == ["customer_id"]


def test_planned_task_rejects_missing_required_arg_without_missing_field() -> None:
    with pytest.raises(ValidationError, match="customer_id"):
        PlannedTask(
            id="task-1",
            agent="invoice",
            intent="latest_invoice",
            instruction="Get latest invoice",
            args={},
            missing_fields=[],
        )


def test_planned_task_rejects_invalid_agent_intent_pair() -> None:
    with pytest.raises(ValidationError, match="not valid for invoice agent"):
        PlannedTask(
            id="task-1",
            agent="invoice",
            intent="tracks_by_artist",
            instruction="Find tracks by artist AC/DC",
            args={"artist": "AC/DC"},
            missing_fields=[],
        )


def test_planned_task_accepts_clarify_music_search_with_missing_search_type() -> None:
    task = PlannedTask(
        id="task-1",
        agent="music",
        intent="clarify_music_search",
        instruction="Ask whether the user wants music by artist or by genre.",
        args={},
        missing_fields=["music_search_type"],
    )

    assert task.intent == "clarify_music_search"


def test_planned_task_accepts_music_query() -> None:
    task = PlannedTask(
        id="task-1",
        agent="music",
        intent="music_query",
        instruction="Find tracks by artist AC/DC",
        args={"search_type": "artist", "artist": "AC/DC"},
        missing_fields=[],
    )

    assert task.args == {
        "search_type": "artist",
        "artist": "AC/DC",
    }


def test_planned_task_rejects_clarify_music_search_without_missing_search_type() -> None:
    with pytest.raises(ValidationError, match="music_search_type"):
        PlannedTask(
            id="task-1",
            agent="music",
            intent="clarify_music_search",
            instruction="Ask whether the user wants music by artist or by genre.",
            args={},
            missing_fields=[],
        )


def test_planned_task_rejects_blank_instruction() -> None:
    with pytest.raises(ValidationError, match="instruction must not be blank"):
        PlannedTask(
            id="task-1",
            agent="music",
            intent="songs_by_genre",
            instruction=" ",
            args={"genre": "Jazz"},
            missing_fields=[],
        )


def test_planner_output_accepts_unrelated_query_with_no_tasks() -> None:
    output = PlannerOutput(
        status="completed",
        tasks=[],
        confidence=0.8,
        requires_aggregation=False,
        missing_fields=[],
    )

    assert output.tasks == []


def test_planner_output_rejects_confidence_out_of_range() -> None:
    with pytest.raises(ValidationError):
        PlannerOutput(
            status="completed",
            tasks=[],
            confidence=1.5,
            requires_aggregation=False,
            missing_fields=[],
        )


def test_planner_output_rejects_multiple_tasks_without_aggregation() -> None:
    with pytest.raises(ValidationError, match="requires_aggregation"):
        PlannerOutput(
            status="completed",
            tasks=[
                {
                    "id": "task-1",
                    "agent": "invoice",
                    "intent": "latest_invoice",
                    "instruction": "Get latest invoice for customer_id=5",
                    "args": {"customer_id": "5"},
                    "missing_fields": [],
                },
                {
                    "id": "task-2",
                    "agent": "music",
                    "intent": "tracks_by_artist",
                    "instruction": "Find tracks by artist AC/DC",
                    "args": {"artist": "AC/DC"},
                    "missing_fields": [],
                },
            ],
            confidence=0.9,
            requires_aggregation=False,
            missing_fields=[],
        )


def test_planner_output_allows_task_missing_fields_before_normalization() -> None:
    output = PlannerOutput(
        status="completed",
        tasks=[
            {
                "id": "task-1",
                "agent": "invoice",
                "intent": "latest_invoice",
                "instruction": "Ask for customer_id",
                "args": {},
                "missing_fields": ["customer_id"],
            }
        ],
        confidence=0.9,
        requires_aggregation=False,
        missing_fields=[],
    )

    assert output.tasks[0].missing_fields == ["customer_id"]
    assert output.missing_fields == []


def test_planner_output_accepts_task_missing_fields_when_propagated_top_level() -> None:
    output = PlannerOutput(
        status="completed",
        tasks=[
            {
                "id": "task-1",
                "agent": "invoice",
                "intent": "latest_invoice",
                "instruction": "Ask for customer_id",
                "args": {},
                "missing_fields": ["customer_id"],
            }
        ],
        confidence=0.9,
        requires_aggregation=False,
        missing_fields=["customer_id"],
    )

    assert output.missing_fields == ["customer_id"]
