import pytest

from multi_agent_system.planner.agent import PlannerAgent
from multi_agent_system.planner.schemas import PlannedTask, PlannerOutput


class FakeStructuredLLM:
    def invoke(self, messages: list) -> PlannerOutput:
        return PlannerOutput(
            tasks=[
                PlannedTask(
                    agent="invoice",
                    intent="latest_invoice",
                    instruction="Get latest invoice for customer_id=5",
                    missing_fields=[],
                )
            ],
            confidence=1.0,
        )


class FakeLLM:
    def with_structured_output(self, schema):
        assert schema is PlannerOutput
        return FakeStructuredLLM()


class FakeEmptyStructuredLLM:
    def invoke(self, messages: list) -> PlannerOutput:
        return PlannerOutput(tasks=[], confidence=0.0)


class FakeEmptyLLM:
    def with_structured_output(self, schema):
        assert schema is PlannerOutput
        return FakeEmptyStructuredLLM()


def test_planner_agent_rejects_disabled_llm() -> None:
    with pytest.raises(ValueError, match="LLM-only"):
        PlannerAgent(use_llm=False)


def test_planner_agent_rejects_deterministic_fallback() -> None:
    with pytest.raises(ValueError, match="fallback has been removed"):
        PlannerAgent(fallback_to_deterministic=True)


def test_planner_agent_invokes_structured_llm(monkeypatch) -> None:
    monkeypatch.setattr(
        "multi_agent_system.planner.agent.get_llm",
        lambda: FakeLLM(),
    )

    planner = PlannerAgent()
    output = planner.invoke("Get latest invoice for customer_id=5")

    assert output.missing_fields == []
    assert output.requires_aggregation is False
    assert len(output.tasks) == 1
    assert output.tasks[0].agent == "invoice"
    assert output.tasks[0].intent == "latest_invoice"


def test_planner_agent_allows_llm_to_return_no_tasks(monkeypatch) -> None:
    monkeypatch.setattr(
        "multi_agent_system.planner.agent.get_llm",
        lambda: FakeEmptyLLM(),
    )

    planner = PlannerAgent()
    output = planner.invoke("What is the weather tomorrow?")

    assert output.tasks == []
    assert output.missing_fields == []
    assert output.requires_aggregation is False
