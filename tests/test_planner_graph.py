import asyncio

from multi_agent_system.planner_app.graph import planner_graph


async def run_case(user_input: str) -> None:
    result = await planner_graph.ainvoke(
        {
            "user_input": user_input,
            "invoice_result": None,
            "music_result": None,
            "final_answer": None,
        }
    )

    print("\nUSER:", user_input)
    print("FINAL ANSWER:")
    print(result["final_answer"])


async def main() -> None:
    await run_case("Get latest invoice for customer_id=5")
    await run_case("Find tracks by artist AC/DC")
    await run_case("Get latest invoice for customer_id=5 and find tracks by artist AC/DC")
    await run_case("What is my latest invoice?")


if __name__ == "__main__":
    asyncio.run(main())