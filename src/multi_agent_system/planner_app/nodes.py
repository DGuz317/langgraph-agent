from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient
from multi_agent_system.a2a_client.music_client import MusicA2AClient
from multi_agent_system.planner.agent import PlannerAgent
from multi_agent_system.planner_app.state import PlannerAppState
from multi_agent_system.planner_app.hitl import interrupt_for_missing_info


planner = PlannerAgent()


def planner_node(state: PlannerAppState) -> dict:
    output = planner.invoke(state["user_input"])

    return {
        "planner_output": output.model_dump(),
        "missing_fields": output.missing_fields,
    }


def missing_info_node(state: PlannerAppState) -> dict:
    missing_fields = state.get("missing_fields", [])
    extracted = interrupt_for_missing_info(missing_fields)

    planner_output = state["planner_output"]
    tasks = planner_output["answer"]

    for task in tasks:
        if task["agent"] == "invoice" and extracted.get("customer_id"):
            task["instruction"] = f"Get latest invoice for customer_id={extracted['customer_id']}"
            task["required_fields"] = []

        if task["agent"] == "music" and extracted.get("artist"):
            task["instruction"] = f"Find tracks by artist {extracted['artist']}"
            task["required_fields"] = []

        if task["agent"] == "music" and extracted.get("genre"):
            task["instruction"] = f"Recommend {extracted['genre']} songs"
            task["required_fields"] = []

    return {
        **extracted,
        "planner_output": planner_output,
        "missing_fields": [],
    }


async def invoice_node(state: PlannerAppState) -> dict:
    client = InvoiceA2AClient()
    planner_output = state["planner_output"]

    invoice_task = next(
        task for task in planner_output["answer"]
        if task["agent"] == "invoice"
    )

    result = await client.ask(invoice_task["instruction"])

    return {
        "invoice_result": result,
    }


async def music_node(state: PlannerAppState) -> dict:
    client = MusicA2AClient()
    planner_output = state["planner_output"]

    music_task = next(
        task for task in planner_output["answer"]
        if task["agent"] == "music"
    )

    result = await client.ask(music_task["instruction"])

    return {
        "music_result": result,
    }


def final_response_node(state: PlannerAppState) -> dict:
    invoice_result = state.get("invoice_result")
    music_result = state.get("music_result")

    if invoice_result and music_result:
        return {
            "final_answer": (
                f"Invoice result:\n{invoice_result}\n\n"
                f"Music result:\n{music_result}"
            )
        }

    if invoice_result:
        return {"final_answer": invoice_result}

    if music_result:
        return {"final_answer": music_result}

    return {
        "final_answer": "I could not complete the request."
    }