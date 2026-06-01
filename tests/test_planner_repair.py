import pytest

from multi_agent_system.planner.agent import PlannerAgent
from multi_agent_system.planner.schemas import PlannerOutput


class RepairablePlannerAgent(PlannerAgent):
    def __init__(self, first_output, repair_output) -> None:
        self.first_output = first_output
        self.repair_output = repair_output
        self.repair_called = False

    async def _invoke_planner_once(
        self,
        user_input: str,
        *,
        memory_context: str | None = None,
    ) -> PlannerOutput:
        return self._coerce_planner_output(self.first_output)

    async def _repair_planner_output(
        self,
        *,
        user_input: str,
        error: Exception,
        memory_context: str | None = None,
    ) -> PlannerOutput:
        self.repair_called = True
        return self._coerce_planner_output(self.repair_output)


class FailingPlannerAgent(PlannerAgent):
    def __init__(self) -> None:
        self.repair_called = False

    async def _invoke_planner_once(
        self,
        user_input: str,
        *,
        memory_context: str | None = None,
    ) -> PlannerOutput:
        raise ValueError("first planner attempt failed")

    async def _repair_planner_output(
        self,
        *,
        user_input: str,
        error: Exception,
        memory_context: str | None = None,
    ) -> PlannerOutput:
        self.repair_called = True
        raise ValueError("repair planner attempt failed")


@pytest.mark.anyio
async def test_planner_repairs_invalid_dispatch_output() -> None:
    planner = RepairablePlannerAgent(
        first_output={
            "status": "completed",
            "tasks": [
                {
                    "agent": "music",
                    "instruction": "",
                    "missing_fields": [],
                }
            ],
            "confidence": 0.9,
            "requires_aggregation": False,
        },
        repair_output={
            "status": "completed",
            "tasks": [
                {
                    "agent": "music",
                    "instruction": "Find tracks by artist AC/DC.",
                    "missing_fields": [],
                }
            ],
            "confidence": 0.9,
            "requires_aggregation": False,
        },
    )

    output = await planner.ainvoke("Find tracks by artist AC/DC")

    assert planner.repair_called is True
    assert output.status == "completed"
    assert output.tasks[0].instruction == "Find tracks by artist AC/DC."


@pytest.mark.anyio
async def test_planner_returns_safe_failed_output_when_repair_fails() -> None:
    planner = FailingPlannerAgent()

    output = await planner.ainvoke("Find tracks by artist AC/DC")

    assert planner.repair_called is True
    assert output.status == "failed"
    assert output.tasks == []
    assert output.confidence == 0.0
    assert output.requires_aggregation is False
    assert output.missing_fields == []


def test_repair_prompt_contains_original_input_and_error() -> None:
    planner = FailingPlannerAgent()

    prompt = planner._build_repair_prompt(
        user_input="Recommend some songs",
        error=ValueError("blank instruction"),
    )

    assert "Recommend some songs" in prompt
    assert "blank instruction" in prompt
    assert "agent, instruction, missing_fields" in prompt
