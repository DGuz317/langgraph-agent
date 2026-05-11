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

    print("Multi Agent System Planner")
    print("Type 'exit' to quit.\n")

    waiting_for_resume = False

    while True:
        user_input = input("User: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            break

        if not user_input:
            continue

        if waiting_for_resume:
            result = await planner_graph.ainvoke(
                Command(resume=user_input),
                config=config,
            )
            waiting_for_resume = False
        else:
            result = await planner_graph.ainvoke(
                {
                    "user_input": user_input,
                    "invoice_result": None,
                    "music_result": None,
                    "final_answer": None,
                },
                config=config,
            )

        interrupts = result.get("__interrupt__")

        if interrupts:
            interrupt_value = interrupts[0].value
            question = interrupt_value.get(
                "question",
                "Could you provide the missing information?",
            )

            print(f"Assistant: {question}\n")
            waiting_for_resume = True
            continue

        print(f"Assistant:\n{result['final_answer']}\n")


if __name__ == "__main__":
    asyncio.run(main())