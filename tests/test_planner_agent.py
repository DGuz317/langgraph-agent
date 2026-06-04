import pytest

from multi_agent_system.planner.agent import PlannerAgent
from multi_agent_system.planner.schemas import PlannedTask, PlannerOutput


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
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> PlannerOutput:
        return self._coerce_planner_output(self.first_output)

    async def _repair_planner_output(
        self,
        *,
        user_input: str,
        error: Exception,
        memory_context: str | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
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
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> PlannerOutput:
        raise ValueError("first planner attempt failed")

    async def _repair_planner_output(
        self,
        *,
        user_input: str,
        error: Exception,
        memory_context: str | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> PlannerOutput:
        self.repair_called = True
        raise ValueError("repair planner attempt failed")


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
                instruction="Ask which music search the user wants.",
                missing_fields=["music_search_type"],
                status="completed",
            )
        ],
        confidence=1.0,
        requires_aggregation=False,
    )

    result = planner._normalize_output(output)

    assert result.tasks[0].id
    assert result.tasks[0].status == "not_started"
    assert result.missing_fields == ["music_search_type"]


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


@pytest.mark.anyio
async def test_planner_passes_same_thread_messages_as_chat_history(monkeypatch) -> None:
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
        "my customer id is 3",
        conversation_messages=[
            {"role": "user", "content": "show me 2 most recent invoice"},
            {"role": "assistant", "content": "Could you provide the customer id?"},
            {"role": "user", "content": "my customer id is 3"},
        ],
    )

    assert [message.type for message in fake_llm.messages] == [
        "system",
        "system",
        "human",
        "ai",
        "human",
    ]
    assert "latest user message" in fake_llm.messages[1].content
    assert fake_llm.messages[-1].content == "my customer id is 3"


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
