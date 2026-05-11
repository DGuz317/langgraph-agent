import asyncio
from uuid import uuid4

from langgraph.types import Command

from multi_agent_system.planner_app.graph import planner_graph


async def main() -> None:
    thread_id = str(uuid4())
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    first = await planner_graph.ainvoke(
        {
            "user_input": "What is my latest invoice?",
            "invoice_result": None,
            "music_result": None,
            "final_answer": None,
        },
        config=config,
    )

    print("FIRST RESULT:")
    print(first)

    second = await planner_graph.ainvoke(
        Command(resume="my id is 5"),
        config=config,
    )

    print("\nSECOND RESULT:")
    print(second["final_answer"])


if __name__ == "__main__":
    asyncio.run(main())