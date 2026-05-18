import asyncio
from uuid import uuid4

from langgraph.types import Command

from multi_agent_system.planner_app.checkpointing import (
    build_async_checkpointer_context,
)
from multi_agent_system.planner_app.graph import build_graph


def _has_interrupt(result: dict) -> bool:
    return "__interrupt__" in result


def _extract_interrupt_message(result: dict) -> str:
    interrupts = result.get("__interrupt__", [])

    if not interrupts:
        return "Could you provide the missing information?"

    first_interrupt = interrupts[0]
    value = getattr(first_interrupt, "value", first_interrupt)

    if isinstance(value, dict):
        return str(value.get("question", value))

    return str(value)


def _extract_final_answer(result: dict) -> str:
    return (
        result.get("final_answer")
        or result.get("answer")
        or "I could not complete the request."
    )


async def main() -> None:
    async with build_async_checkpointer_context() as checkpointer:
        planner_graph = build_graph(checkpointer=checkpointer)

        print("Multi Agent System Planner")
        print("Type 'exit' to quit.")

        active_config: dict | None = None
        waiting_for_resume = False

        while True:
            user_input = input("\nUser: ").strip()

            if user_input.lower() in {"exit", "quit"}:
                break

            try:
                if waiting_for_resume and active_config is not None:
                    result = await planner_graph.ainvoke(
                        Command(resume=user_input),
                        config=active_config,
                    )
                else:
                    active_config = {
                        "configurable": {
                            "thread_id": str(uuid4()),
                        }
                    }
                    result = await planner_graph.ainvoke(
                        {"user_input": user_input},
                        config=active_config,
                    )

                print("Assistant:")

                if _has_interrupt(result):
                    waiting_for_resume = True
                    print(_extract_interrupt_message(result))
                    continue

                waiting_for_resume = False
                active_config = None
                print(_extract_final_answer(result))

            except Exception as exc:
                waiting_for_resume = False
                active_config = None
                print("Assistant:")
                print(f"System error: {exc}")


if __name__ == "__main__":
    asyncio.run(main())