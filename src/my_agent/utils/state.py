from typing import TypedDict, List
from my_agent.utils.constants import STATUS_SUCCESS, STATUS_FAIL


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
    status: Literal[STATUS_SUCCESS, STATUS_FAIL]
    result: dict | None
    error: str | None


class AppState(TypedDict):
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