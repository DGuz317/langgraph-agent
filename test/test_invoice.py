import pytest
import asyncio
import uuid

from conftest import agents


@pytest.mark.asyncio
async def test_invoice_agent_single(agents):
    agent = agents["invoice_agent"]

    thread_id = str(uuid.uuid4())

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Get invoices sorted by unit price for customer 5"
                }
            ]
        },
        config={"configurable": {"thread_id": f"{thread_id}:invoice"}}
    )

    assert "structured_response" in result

    output = result["structured_response"]

    assert output.status == "completed"
    assert output.answer is not None
    assert 0 <= output.confidence <= 1
