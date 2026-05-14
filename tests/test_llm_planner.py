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
    "recommend some rock tracks",
    "Check for song Rolling in the Deep",
]


HITL_CASES = [
    (
        "what is my latest invoice?\n\n"
        "Additional information collected from the user: customer_id=5",
        "invoice",
        "latest_invoice",
        "customer_id",
        "5",
    ),
    (
        "show albums\n\n"
        "Additional information collected from the user: artist=Queen",
        "music",
        "albums_by_artist",
        "artist",
        "Queen",
    ),
    (
        "check for song\n\n"
        "Additional information collected from the user: song_title=Ligia",
        "music",
        "check_song",
        "song_title",
        "Ligia",
    ),
]


def test_llm_planner_returns_structured_tasks_for_core_cases() -> None:
    from multi_agent_system.planner.agent import PlannerAgent

    planner = PlannerAgent(
        use_llm=True,
        fallback_to_deterministic=False,
    )

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

    planner = PlannerAgent(
        use_llm=True,
        fallback_to_deterministic=False,
    )

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
