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
async def test_planner_repairs_invalid_agent_intent_pair() -> None:
    planner = RepairablePlannerAgent(
        first_output={
            "status": "completed",
            "tasks": [
                {
                    "id": "task-1",
                    "agent": "invoice",
                    "intent": "tracks_by_artist",
                    "instruction": "Find tracks by artist AC/DC",
                    "args": {"artist": "AC/DC"},
                    "missing_fields": [],
                    "status": "not_started",
                }
            ],
            "confidence": 0.9,
            "requires_aggregation": False,
            "missing_fields": [],
        },
        repair_output={
            "status": "completed",
            "tasks": [
                {
                    "id": "task-1",
                    "agent": "music",
                    "intent": "tracks_by_artist",
                    "instruction": "Find tracks by artist AC/DC",
                    "args": {"artist": "AC/DC"},
                    "missing_fields": [],
                    "status": "not_started",
                }
            ],
            "confidence": 0.9,
            "requires_aggregation": False,
            "missing_fields": [],
        },
    )

    output = await planner.ainvoke("Find tracks by artist AC/DC")

    assert planner.repair_called is True
    assert output.status == "completed"
    assert output.tasks[0].agent == "music"
    assert output.tasks[0].intent == "tracks_by_artist"


@pytest.mark.anyio
async def test_planner_repairs_missing_required_arg_with_hitl_missing_field() -> None:
    planner = RepairablePlannerAgent(
        first_output={
            "status": "completed",
            "tasks": [
                {
                    "id": "task-1",
                    "agent": "invoice",
                    "intent": "latest_invoice",
                    "instruction": "Get latest invoice",
                    "args": {},
                    "missing_fields": [],
                    "status": "not_started",
                }
            ],
            "confidence": 0.9,
            "requires_aggregation": False,
            "missing_fields": [],
        },
        repair_output={
            "status": "completed",
            "tasks": [
                {
                    "id": "task-1",
                    "agent": "invoice",
                    "intent": "latest_invoice",
                    "instruction": "Ask for customer_id",
                    "args": {},
                    "missing_fields": ["customer_id"],
                    "status": "not_started",
                }
            ],
            "confidence": 0.9,
            "requires_aggregation": False,
            "missing_fields": ["customer_id"],
        },
    )

    output = await planner.ainvoke("What is my latest invoice?")

    assert planner.repair_called is True
    assert output.status == "completed"
    assert output.tasks[0].missing_fields == ["customer_id"]
    assert output.missing_fields == ["customer_id"]


@pytest.mark.anyio
async def test_planner_repairs_generic_music_request_to_clarify_search() -> None:
    planner = RepairablePlannerAgent(
        first_output={
            "status": "completed",
            "tasks": [
                {
                    "id": "task-1",
                    "agent": "music",
                    "intent": "songs_by_genre",
                    "instruction": "Recommend some songs",
                    "args": {},
                    "missing_fields": [],
                    "status": "not_started",
                }
            ],
            "confidence": 0.7,
            "requires_aggregation": False,
            "missing_fields": [],
        },
        repair_output={
            "status": "completed",
            "tasks": [
                {
                    "id": "task-1",
                    "agent": "music",
                    "intent": "clarify_music_search",
                    "instruction": "Ask whether the user wants music by artist or by genre.",
                    "args": {},
                    "missing_fields": ["music_search_type"],
                    "status": "not_started",
                }
            ],
            "confidence": 0.8,
            "requires_aggregation": False,
            "missing_fields": ["music_search_type"],
        },
    )

    output = await planner.ainvoke("Recommend some songs")

    assert planner.repair_called is True
    assert output.tasks[0].intent == "clarify_music_search"
    assert output.tasks[0].missing_fields == ["music_search_type"]


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
        error=ValueError("missing music_search_type"),
    )

    assert "Recommend some songs" in prompt
    assert "missing music_search_type" in prompt
    assert "clarify_music_search" in prompt
    assert "tasks=[]" in prompt
