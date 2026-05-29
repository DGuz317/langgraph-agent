import pytest

from multi_agent_system.planner.agent import PlannerAgent
from multi_agent_system.planner.schemas import PlannedTask, PlannerOutput


def test_normalize_output_adds_task_id_and_sets_status(monkeypatch) -> None:
    monkeypatch.setattr(
        "multi_agent_system.planner.agent.get_llm",
        lambda: object(),
    )

    planner = PlannerAgent()

    output = PlannerOutput(
        status="completed",
        tasks=[
            PlannedTask(
                id="",
                agent="music",
                intent="clarify_music_search",
                instruction="Ask whether the user wants music by artist or by genre.",
                args={},
                missing_fields=["music_search_type"],
                status="completed",
            )
        ],
        confidence=1.0,
        requires_aggregation=False,
        missing_fields=[],
    )

    result = planner._normalize_output(output)

    assert result.status == "completed"
    assert result.tasks[0].id
    assert result.tasks[0].status == "not_started"
    assert result.missing_fields == ["music_search_type"]

def test_normalize_output_preserves_task_args(monkeypatch) -> None:
    monkeypatch.setattr(
        "multi_agent_system.planner.agent.get_llm",
        lambda: object(),
    )

    planner = PlannerAgent()

    output = PlannerOutput(
        status="completed",
        tasks=[
            PlannedTask(
                id="task_1",
                agent="music",
                intent="songs_by_genre",
                instruction="Recommend songs by genre rock",
                args={"genre": "rock"},
                missing_fields=[],
                status="completed",
            )
        ],
        confidence=1.0,
        requires_aggregation=False,
        missing_fields=[],
    )

    result = planner._normalize_output(output)

    assert result.tasks[0].args == {"genre": "rock"}


@pytest.mark.anyio
async def test_planner_injects_memory_context_as_system_guidance(monkeypatch) -> None:
    class FakeStructuredLLM:
        def __init__(self) -> None:
            self.messages = []

        async def ainvoke(self, messages):
            self.messages = messages
            return PlannerOutput(
                status="completed",
                tasks=[],
                confidence=1.0,
                requires_aggregation=False,
                missing_fields=[],
            )

    fake_llm = FakeStructuredLLM()

    class FakeLLM:
        def with_structured_output(self, schema):
            return fake_llm

    monkeypatch.setattr(
        "multi_agent_system.planner.agent.get_llm",
        lambda: FakeLLM(),
    )

    planner = PlannerAgent()
    await planner.ainvoke(
        "Get my latest invoice",
        memory_context="- invoice-memory: latest invoice routes to invoice.",
    )

    assert len(fake_llm.messages) == 3
    assert fake_llm.messages[1].type == "system"
    assert "Relevant sanitized memory skills" in fake_llm.messages[1].content
    assert "Do not invent missing values from memory" in fake_llm.messages[1].content
