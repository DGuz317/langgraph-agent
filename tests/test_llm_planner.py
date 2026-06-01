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
async def test_llm_planner_returns_generic_dispatch_tasks() -> None:
    from multi_agent_system.planner.agent import PlannerAgent

    planner = PlannerAgent()
    output = await planner.ainvoke(
        "Show me 3 most recent invoices for customer id=7 and recommend 5 Jazz songs."
    )

    assert output.status == "completed"
    assert output.requires_aggregation is True
    assert [task.agent for task in output.tasks] == ["invoice", "music"]
    assert "3" in output.tasks[0].instruction
    assert "customer" in output.tasks[0].instruction.lower()
    assert "5" in output.tasks[1].instruction
    assert "jazz" in output.tasks[1].instruction.lower()
    assert not hasattr(output.tasks[0], "args")
