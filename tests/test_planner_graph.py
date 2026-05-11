import asyncio
from uuid import uuid4

from multi_agent_system.planner_app.graph import planner_graph


async def run_case(user_input: str) -> None:
    config = {
        "configurable": {
            "thread_id": str(uuid4()),
        }
    }

    result = await planner_graph.ainvoke(
        {
            "user_input": user_input,
            "invoice_result": None,
            "music_result": None,
            "final_answer": None,
        },
        config=config,
    )

    print("\nUSER:", user_input)

    interrupts = result.get("__interrupt__")
    if interrupts:
        interrupt_value = interrupts[0].value
        print("INTERRUPT:")
        print(interrupt_value)
        return

    print("FINAL ANSWER:")
    print(result["final_answer"])


async def main() -> None:
    await run_case("Get latest invoice for customer_id=5")
    await run_case("Find tracks by artist AC/DC")
    await run_case("Get latest invoice for customer_id=5 and find tracks by artist AC/DC")
    await run_case("What is my latest invoice?")


if __name__ == "__main__":
    asyncio.run(main())