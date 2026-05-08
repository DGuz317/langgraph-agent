import asyncio
from importlib import import_module
from typing import Any

from my_agent.utils.state import AppState


class _UnavailableService:
    """Fallback used while service modules are still scaffolds."""

    def __init__(self, service_name: str, original_exc: Exception):
        self._service_name = service_name
        self._original_exc = original_exc

    async def plan(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError(f"{self._service_name} is unavailable") from self._original_exc

    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError(f"{self._service_name} is unavailable") from self._original_exc

    async def aggregate(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError(f"{self._service_name} is unavailable") from self._original_exc


def _load_service(module_name: str, class_name: str) -> Any:
    try:
        module = import_module(module_name)
        service_cls = getattr(module, class_name)
        return service_cls()
    except (ImportError, AttributeError) as exc:
        return _UnavailableService(class_name, exc)


planner_service = _load_service("my_agent.services.planner_service", "PlannerService")
task_execution_service = _load_service(
    "my_agent.services.task_execution_service", "TaskExecutionService"
)
aggregator_service = _load_service(
    "my_agent.services.aggregator_service", "AggregatorService"
)


async def planner_node(state: AppState) -> dict:
    """
    Generate executable tasks from the latest user message.
    """
    user_input = _last_user_message(state)

    tasks = await planner_service.plan(user_input=user_input)

    return {"tasks": tasks}


async def execute_tasks_node(state: AppState) -> dict:
    """
    Execute planned tasks against remote A2A agents.
    """
    tasks = state.get("tasks", [])

    if not tasks:
        return {"results": []}

    results = await asyncio.gather(
        *(task_execution_service.execute(task=task) for task in tasks)
    )

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
