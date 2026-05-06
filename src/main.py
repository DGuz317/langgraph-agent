import asyncio
import uuid

from agent_app.orchestrator.runtime import AgentRuntime


# async def test_invoice(rt):
#     print("\n=== TEST: INVOICE AGENT ===")

#     agent = rt.agents["invoice_agent"]
#     thread_id = str(uuid.uuid4())

#     result = await agent.ainvoke(
#         {
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": "Get invoices sorted by unit price for customer 5",
#                 }
#             ]
#         },
#         config={"configurable": {"thread_id": thread_id}},
#     )

#     print(result["messages"][-1].content)


# async def test_planner(rt):
#     print("\n=== TEST: PLANNER ===")

#     agent = rt.agents["planner"]
#     thread_id = str(uuid.uuid4())

#     result = await agent.ainvoke(
#         {
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": "Get AC/DC tracks and invoices for customer 5",
#                 }
#             ]
#         },
#         config={"configurable": {"thread_id": thread_id}},
#     )

#     print(result["structured_response"])


async def test_orchestrator(rt):
    print("\n=== TEST: ORCHESTRATOR ===")

    graph = rt.graph
    thread_id = str(uuid.uuid4())

    result = await graph.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Get AC/DC tracks and invoices for customer 5",
                }
            ],
            "thread_id": thread_id,
        },
        config={"configurable": {"thread_id": thread_id}},
    )

    print(result["final_answer"])


async def main():
    rt = AgentRuntime()

    await rt.start()   # ✅ ONE session

    try:
        # await test_invoice(rt)
        # await test_planner(rt)
        await test_orchestrator(rt)
    finally:
        await rt.stop()   # ✅ clean shutdown (safe here)


if __name__ == "__main__":
    asyncio.run(main())