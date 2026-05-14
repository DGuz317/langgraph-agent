import os

import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LLM_TESTS") != "1",
    reason="Set RUN_LLM_TESTS=1 and make sure the configured LLM is running to run these tests.",
)


CASES = [
    "Get latest invoice for customer_id=5",
    "Find tracks by artist AC/DC",
    "Get latest invoice for customer_id=5 and find tracks by artist AC/DC",
    "What is my latest invoice?",
    "recommend some tracks",
    "recommend some songs",
    "Check for song Rolling in the Deep",
]


HITL_CASES = [
    (
        "Original user request: what is my latest invoice?\n"
        "User follow-up answer: 5\n"
        "Structured values extracted from the follow-up: customer_id=5\n"
        "Re-plan the original request using the follow-up answer as free-form context. "
        "Do not assume the answer belongs to the previously requested field if another "
        "interpretation better fits the original request.",
        "invoice",
        "latest_invoice",
        "customer_id",
        "5",
    ),
    (
        "Original user request: show albums\n"
        "User follow-up answer: Queen\n"
        "Re-plan the original request using the follow-up answer as free-form context. "
        "Do not assume the answer belongs to the previously requested field if another "
        "interpretation better fits the original request.",
        "music",
        "albums_by_artist",
        "artist",
        "Queen",
    ),
    (
        "Original user request: check for song\n"
        "User follow-up answer: Ligia\n"
        "Re-plan the original request using the follow-up answer as free-form context. "
        "Do not assume the answer belongs to the previously requested field if another "
        "interpretation better fits the original request.",
        "music",
        "check_song",
        "song_title",
        "Ligia",
    ),
    (
        "Original user request: recommend some songs\n"
        "User follow-up answer: AC/DC\n"
        "Re-plan the original request using the follow-up answer as free-form context. "
        "Do not assume the answer belongs to the previously requested field if another "
        "interpretation better fits the original request.",
        "music",
        "tracks_by_artist",
        "artist",
        "AC/DC",
    ),
]


def test_llm_planner_returns_structured_tasks_for_core_cases() -> None:
    from multi_agent_system.planner.agent import PlannerAgent

    planner = PlannerAgent()

    for user_input in CASES:
        output = planner.invoke(user_input)
        data = output.model_dump()

        assert isinstance(data.get("tasks"), list), user_input
        assert data["tasks"], user_input
        assert isinstance(data.get("missing_fields"), list), user_input

        for task in data["tasks"]:
            assert task["agent"] in {"invoice", "music"}, user_input
            assert isinstance(task.get("instruction"), str), user_input
            assert task["instruction"].strip(), user_input
            assert isinstance(task.get("missing_fields", []), list), user_input


def test_llm_planner_accepts_hitl_context_for_replanning() -> None:
    from multi_agent_system.planner.agent import PlannerAgent

    planner = PlannerAgent()

    for user_input, expected_agent, expected_intent, field, value in HITL_CASES:
        output = planner.invoke(user_input)
        data = output.model_dump()

        matching_tasks = [
            task
            for task in data["tasks"]
            if task["agent"] == expected_agent and task["intent"] == expected_intent
        ]

        assert matching_tasks, user_input

        task = matching_tasks[0]
        instruction = task["instruction"].lower()

        assert value.lower() in instruction, user_input
        assert field not in task.get("missing_fields", []), user_input

def test_llm_planner_marks_generic_music_recommendation_as_ambiguous() -> None:
    from multi_agent_system.planner.agent import PlannerAgent

    planner = PlannerAgent()

    output = planner.invoke("recommend some songs")

    assert output.tasks
    assert output.tasks[0].agent == "music"
    assert output.tasks[0].intent == "clarify_music_search"
    assert output.tasks[0].missing_fields == ["music_search_type"]
    assert output.missing_fields == ["music_search_type"]
