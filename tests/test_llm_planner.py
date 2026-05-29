import os

import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LLM_TESTS") != "1",
    reason="LLM planner tests require RUN_LLM_TESTS=1",
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_llm_planner_returns_structured_tasks_for_core_cases() -> None:
    from multi_agent_system.planner.agent import PlannerAgent

    planner = PlannerAgent()

    cases = [
        {
            "user_input": "Get latest invoice for customer_id=5",
            "agent": "invoice",
            "intent": "invoice_query",
            "missing_fields": [],
            "args": {"customer_id": "5", "include_support_employee": "true"},
        },
        {
            "user_input": "Show invoice detail for invoice_id=361",
            "agent": "invoice",
            "intent": "invoice_query",
            "missing_fields": [],
            "args": {"invoice_id": "361", "include_support_employee": "true"},
        },
        {
            "user_input": "Show total invoice spending for customer_id=5",
            "agent": "invoice",
            "intent": "invoice_summary",
            "missing_fields": [],
            "args": {"customer_id": "5"},
        },
        {
            "user_input": "Who is my support employee for customer_id=5?",
            "agent": "invoice",
            "intent": "customer_support_employee",
            "missing_fields": [],
            "args": {"customer_id": "5"},
        },
        {
            "user_input": "What is my latest invoice?",
            "agent": "invoice",
            "intent": "invoice_query",
            "missing_fields": ["customer_id"],
            "args": {},
        },
        {
            "user_input": "Get invoices sorted by unit price for customer_id=5",
            "agent": "invoice",
            "intent": "invoice_query",
            "missing_fields": [],
            "args": {
                "customer_id": "5",
                "sort_by": "unit_price",
                "include_support_employee": "true",
            },
        },
        {
            "user_input": "All my invoice information of customer id 5",
            "agent": "invoice",
            "intent": "invoice_query",
            "missing_fields": [],
            "args": {"customer_id": "5", "include_support_employee": "true"},
        },
        {
            "user_input": "Who is the support employee for latest invoice of customer id 5?",
            "agent": "invoice",
            "intent": "invoice_query",
            "missing_fields": [],
            "args": {"customer_id": "5", "include_support_employee": "true"},
        },
        {
            "user_input": "Show my invoices sorted by unit price",
            "agent": "invoice",
            "intent": "invoice_query",
            "missing_fields": ["customer_id"],
            "args": {},
        },
        {
            "user_input": "Find tracks by artist AC/DC",
            "agent": "music",
            "intent": "music_query",
            "missing_fields": [],
            "args": {"search_type": "artist", "artist": "AC/DC"},
        },
        {
            "user_input": "recommend some rock tracks",
            "agent": "music",
            "intent": "music_query",
            "missing_fields": [],
            "args": {"search_type": "genre", "genre": "rock"},
        },
        {
            "user_input": "Check for song Ligia",
            "agent": "music",
            "intent": "music_query",
            "missing_fields": [],
            "args": {"search_type": "song_title", "song_title": "Ligia"},
        },
    ]

    for case in cases:
        output = await planner.ainvoke(case["user_input"])

        assert output.status == "completed"
        assert len(output.tasks) == 1

        task = output.tasks[0]

        assert task.agent == case["agent"]
        assert task.intent == case["intent"]
        assert task.missing_fields == case["missing_fields"]
        assert output.missing_fields == case["missing_fields"]

        for key, value in case["args"].items():
            assert task.args.get(key) == value


@pytest.mark.anyio
async def test_llm_planner_marks_generic_music_recommendation_as_ambiguous() -> None:
    from multi_agent_system.planner.agent import PlannerAgent

    planner = PlannerAgent()

    ambiguous_inputs = [
        "recommend some songs",
        "recommend some tracks",
        "find some music",
        "suggest songs",
    ]

    for user_input in ambiguous_inputs:
        output = await planner.ainvoke(user_input)

        assert output.status == "completed"
        assert len(output.tasks) == 1

        task = output.tasks[0]

        assert task.agent == "music"
        assert task.intent == "clarify_music_search"
        assert task.instruction == "Ask whether the user wants music by artist or by genre."
        assert task.args == {}
        assert task.missing_fields == ["music_search_type"]
        assert output.missing_fields == ["music_search_type"]
