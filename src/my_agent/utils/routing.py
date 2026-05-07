from my_agent.utils.state import AppState


def should_aggregate(state: AppState) -> str:
    """
    Decide whether aggregation should occur.

    Returns:
        - "aggregate"
        - "end"
    """

    results = state.get("results", [])

    if not results:
        return "end"

    return "aggregate"