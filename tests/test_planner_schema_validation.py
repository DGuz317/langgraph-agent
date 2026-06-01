import pytest
from pydantic import ValidationError

from multi_agent_system.planner.schemas import PlannedTask, PlannerOutput


def test_planned_task_accepts_generic_dispatch_instruction() -> None:
    task = PlannedTask(
        id="task-1",
        agent="invoice",
        instruction=(
            "Show 3 most recent invoices for customer id=7 and include support "
            "employee details."
        ),
    )

    assert task.agent == "invoice"
    assert "customer id=7" in task.instruction
    assert task.missing_fields == []


def test_planned_task_rejects_blank_instruction() -> None:
    with pytest.raises(ValidationError, match="instruction must not be blank"):
        PlannedTask(
            agent="music",
            instruction=" ",
        )


def test_planned_task_normalizes_missing_fields() -> None:
    task = PlannedTask(
        agent="invoice",
        instruction="Ask for a customer id before querying invoices.",
        missing_fields=[" customer_id ", "", None],
    )

    assert task.missing_fields == ["customer_id"]


def test_planner_output_requires_aggregation_for_multiple_tasks() -> None:
    with pytest.raises(ValidationError, match="requires_aggregation"):
        PlannerOutput(
            status="completed",
            tasks=[
                PlannedTask(agent="invoice", instruction="Show invoices."),
                PlannedTask(agent="music", instruction="Recommend Jazz songs."),
            ],
            confidence=1.0,
            requires_aggregation=False,
        )


def test_planner_output_accepts_multi_agent_dispatch() -> None:
    output = PlannerOutput(
        status="completed",
        tasks=[
            PlannedTask(
                agent="invoice",
                instruction="Show invoices for customer id=7.",
            ),
            PlannedTask(
                agent="music",
                instruction="Recommend 5 Jazz songs.",
            ),
        ],
        confidence=1.0,
        requires_aggregation=True,
    )

    assert [task.agent for task in output.tasks] == ["invoice", "music"]
