import pytest
import asyncio
import uuid

from conftest import agents


@pytest.mark.asyncio
async def test_music_agent_single(agents):
    agents = await init_agents()
    agent = agents["music_agent"]

    thread_id = str(uuid.uuid4())

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Get tracks by artist AC/DC"
                }
            ]
        },
        config={"configurable": {"thread_id": f"{thread_id}:music"}}
    )

    assert "structured_response" in result

    output = result["structured_response"]

    assert output.status == "completed"
    assert output.answer is not None
    assert 0 <= output.confidence <= 1