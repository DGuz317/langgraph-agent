import asyncio

from my_agent.services.planner_service import PlannerService
from my_agent.services.aggregator_service import AggregatorService
from my_agent.services.task_execution_service import TaskExecutionService
from my_agent.utils.state import AppState


planner_service = PlannerService()
task_execution_service = TaskExecutionService()
aggregator_service = AggregatorService()


async def planner_node(state: AppState) -> dict:
    """
    Generate executable tasks from the latest user message.
    """
    user_input = _last_user_message(state)
 
    tasks = await planner_service.plan(user_input=user_input)
 
    existing_messages = state.get("messages", [])
    user_message = {"role": "user", "content": user_input}
    updated_messages = existing_messages + [user_message]
 
    return {
        "tasks": tasks,
        "messages": updated_messages,
    }


async def execute_tasks_node(state: AppState) -> dict:
    """
    Execute planned tasks against remote A2A agents.
    """
    tasks = state.get("tasks", [])
 
    futures = []
    for task in tasks:
        future = asyncio.ensure_future(task_execution_service.execute(task=task))
        futures.append(future)
 
    await asyncio.wait(futures)
 
    results = []
    for future in futures:
        result = future.result()
        results.append(result)
 
    return {"results": results}


async def aggregate_node(state: AppState) -> dict:
    """
    Combine all agent outputs into a final response.
    """
    results = state.get("results", [])
    final_response = await aggregator_service.aggregate(results=results)
 
    existing_messages = state.get("messages", [])
    assistant_message = {"role": "assistant", "content": final_response}
    updated_messages = existing_messages + [assistant_message]
 
    return {
        "final_response": final_response,
        "messages": updated_messages,
    }

# --- Helpers ---
def _last_user_message(state: AppState) -> str:
    """Return the content of the most recent user message, or empty string."""
    for msg in reversed(state.get("messages", [])):
        if msg.get("role") == "user":
            return msg.get("content", "")
    return ""
