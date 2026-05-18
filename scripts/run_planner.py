import asyncio

from multi_agent_system.orchestrator.service import PlannerService
from multi_agent_system.planner_app.checkpointing import (
    build_async_checkpointer_context,
)
from multi_agent_system.planner_app.graph import build_graph


async def main() -> None:
    async with build_async_checkpointer_context() as checkpointer:
        graph = build_graph(checkpointer=checkpointer)
        service = PlannerService(graph=graph)

        print("Multi Agent System Planner")
        print("Type 'exit' to quit.")

        active_thread_id: str | None = None
        waiting_for_resume = False

        while True:
            user_input = input("\nUser: ").strip()

            if user_input.lower() in {"exit", "quit"}:
                break

            if not user_input:
                continue

            response = await service.invoke(
                user_input,
                thread_id=active_thread_id,
                resume=waiting_for_resume,
            )

            print("Assistant:")

            if response.status == "interrupted":
                active_thread_id = response.thread_id
                waiting_for_resume = True
                print(response.interrupt_message)
                continue

            if response.status == "failed":
                active_thread_id = None
                waiting_for_resume = False
                print(response.final_answer or "System error.")
                continue

            active_thread_id = None
            waiting_for_resume = False
            print(response.final_answer or "I could not complete the request.")


if __name__ == "__main__":
    asyncio.run(main())