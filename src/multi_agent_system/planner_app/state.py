from typing import Any, Dict, List, Literal, TypedDict


class Task(TypedDict):
    """
    A single executable task produced by the planner.

    Example:
    {
        "agent": "invoice_agent",
        "query": "Get invoices for customer 2"
    }
    """

    agent: str
    query: str


class AgentResult(TypedDict):
    """
    Normalized response returned by every remote A2A agent.

    IMPORTANT:
    Every agent MUST return this structure.

    This normalization allows:
    - aggregation
    - retries
    - observability
    - parallel execution
    - easier debugging
    """

    agent: str
    status: Literal["success", "fail"]
    result: dict | None
    error: str | None


class AppState(TypedDict, total=False):
    """
    Global LangGraph state shared across all nodes.

    LangGraph nodes incrementally update this state.

    total=False allows partial updates from nodes.
    """
    messages: List[Dict[str, Any]]
    context_id: str | None
    task_id: str | None

    tasks: List[Task]
    results: List[AgentResult]
    final_response: str
