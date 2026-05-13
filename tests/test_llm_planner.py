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
