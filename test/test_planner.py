import pytest
import asyncio
import uuid

from conftest import agents


@pytest.mark.asyncio
async def test_planner_single_intent(agents):
    agents = await init_agents()
    planner = agents["planner"]

    thread_id = str(uuid.uuid4())

    result = await planner.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Get invoices for customer 5"
                }
            ]
        },
        config={"configurable": {"thread_id": f"{thread_id}:planner"}}
    )

    plan = result["structured_response"]

    assert plan.status == "completed"
    assert len(plan.answer) == 1
    assert 0 <= output.confidence <= 1



# multi-intent
# @pytest.mark.asyncio
# async def test_planner_multi_intent():
#     agents = await init_agents()
#     planner = agents["planner"]

#     thread_id = str(uuid.uuid4())

#     result = await planner.ainvoke(
#         {
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": "Get AC/DC tracks and invoices for customer 5"
#                 }
#             ]
#         },
#         config={"configurable": {"thread_id": f"{thread_id}:planner"}}
#     )

#     plan = result["structured_response"]

    # assert plan.status == "completed"
    # assert len(plan.answer) >= 2
    # assert 0 <= output.confidence <= 1