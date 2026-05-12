import asyncio
from uuid import uuid4

from langgraph.types import Command

from multi_agent_system.planner_app.graph import planner_graph


def create_thread_config() -> dict:
    return {
        "configurable": {
            "thread_id": str(uuid4()),
        }
    }


def get_interrupt_question(result: dict) -> str | None:
    interrupts = result.get("__interrupt__")

    if not interrupts:
        return None

    interrupt_value = interrupts[0].value

    if isinstance(interrupt_value, dict):
        return interrupt_value.get(
            "question",
            "Could you provide the missing information?",
        )

    return str(interrupt_value)


async def main() -> None:
    print("Multi Agent System Planner")
    print("Type 'exit' to quit.\n")

    waiting_for_resume = False
    active_config: dict | None = None

    while True:
        user_input = input("User: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            break

        if not user_input:
            continue

        try:
            if waiting_for_resume:
                if active_config is None:
                    raise RuntimeError("Cannot resume without an active graph thread.")

                result = await planner_graph.ainvoke(
                    Command(resume=user_input),
                    config=active_config,
                )
            else:
                active_config = create_thread_config()

                result = await planner_graph.ainvoke(
                    {
                        "user_input": user_input,
                        "invoice_result": None,
                        "music_result": None,
                        "final_answer": None,
                    },
                    config=active_config,
                )

        except Exception as exc:
            print(f"Assistant:\nSystem error: {exc}\n")
            waiting_for_resume = False
            active_config = None
            continue

        interrupt_question = get_interrupt_question(result)

        if interrupt_question:
            print(f"Assistant: {interrupt_question}\n")
            waiting_for_resume = True
            continue

        final_answer = result.get("final_answer", "I could not complete the request.")
        print(f"Assistant:\n{final_answer}\n")

        waiting_for_resume = False
        active_config = None


if __name__ == "__main__":
    asyncio.run(main())