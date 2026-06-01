from uuid import UUID, uuid5

MEMORY_SCOPE = "workflow-outcome-v1"
LEARNING_SPACE_META = {
    "source": "multi_agent_system.planner",
    "memory_scope": MEMORY_SCOPE,
}

_SESSION_NAMESPACE = UUID("cfcd8caa-f533-5ccd-a31c-c695f4f52142")


def acontext_session_id(thread_id: str) -> str:
    """Map a LangGraph thread id into a stable Acontext UUID."""
    return str(uuid5(_SESSION_NAMESPACE, f"planner:{MEMORY_SCOPE}:{thread_id}"))
