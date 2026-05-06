import pytest
import uuid

from agent_app.orchestrator.graph import build_graph


@pytest.mark.asyncio
async def test_full_pipeline(runtime):
    graph = build_graph(runtime.agents)

    thread_id = str(uuid.uuid4())

    result = await graph.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Get AC/DC tracks and invoices for customer 5"
                }
            ],
            "thread_id": thread_id,
            "plan": {},
            "results": [],
            "final_answer": None,
        }
    )

    assert result["final_answer"] is not None