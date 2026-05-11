from multi_agent_system.planner_app.state import PlannerAppState


def route_after_planner(state: PlannerAppState) -> str:
    if state.get("missing_fields"):
        return "missing_info"

    planner_output = state["planner_output"]
    tasks = planner_output["answer"]

    agents = {task["agent"] for task in tasks}

    if agents == {"invoice"}:
        return "invoice"

    if agents == {"music"}:
        return "music"

    if agents == {"invoice", "music"}:
        return "invoice"

    return "final_response"


def route_after_invoice(state: PlannerAppState) -> str:
    planner_output = state["planner_output"]
    tasks = planner_output["answer"]

    has_music_task = any(task["agent"] == "music" for task in tasks)

    if has_music_task and not state.get("music_result"):
        return "music"

    return "final_response"