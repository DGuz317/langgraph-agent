import re

from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient
from multi_agent_system.a2a_client.music_client import MusicA2AClient
from multi_agent_system.planner.agent import PlannerAgent
from multi_agent_system.planner_app.state import PlannerAppState
from multi_agent_system.planner_app.hitl import interrupt_for_missing_info
from multi_agent_system.aggregator.agent import AggregatorAgent
from multi_agent_system.aggregator.schemas import AggregatorInput, AgentResult
from multi_agent_system.planner_app.task_instructions import build_instruction_from_task

planner = PlannerAgent()
aggregator = AggregatorAgent()


def _extract_instruction_number(instruction: str, field_names: list[str]) -> str | None:
    for field_name in field_names:
        pattern = rf"\b{re.escape(field_name)}\s*(?:=|:|is)?\s*(\d+)"
        match = re.search(pattern, instruction, flags=re.IGNORECASE)

        if match:
            return match.group(1)

    return None


def planner_node(state: PlannerAppState) -> dict:
    output = planner.invoke(state["user_input"])

    return {
        "planner_output": output.model_dump(),
        "missing_fields": output.missing_fields,
    }

def _update_task_args(task: dict, values: dict[str, str]) -> None:
    args = task.get("args") or {}
    args.update(values)
    task["args"] = args

def missing_info_node(state: PlannerAppState) -> dict:
    missing_fields = state.get("missing_fields", [])
    extracted = interrupt_for_missing_info(missing_fields)

    planner_output = state["planner_output"]
    tasks = planner_output["tasks"]

    for task in tasks:
        if task["agent"] == "invoice" and extracted.get("customer_id"):
            customer_id = extracted["customer_id"]
            intent = task.get("intent", "latest_invoice")

            task["intent"] = intent
            task["args"] = {"customer_id": customer_id}
            task["instruction"] = build_instruction_from_task(task)
            task["missing_fields"] = []

        if task["agent"] == "music" and extracted.get("artist"):
            task["intent"] = "tracks_by_artist"
            task["args"] = {"artist": extracted["artist"]}
            task["instruction"] = build_instruction_from_task(task)
            task["missing_fields"] = []

        if task["agent"] == "music" and extracted.get("genre"):
            task["intent"] = "songs_by_genre"
            task["args"] = {"genre": extracted["genre"]}
            task["instruction"] = build_instruction_from_task(task)
            task["missing_fields"] = []

        if task["agent"] == "music" and extracted.get("song_title"):
            task["intent"] = "check_song"
            task["args"] = {"song_title": extracted["song_title"]}
            task["instruction"] = build_instruction_from_task(task)
            task["missing_fields"] = []

    return {
        **extracted,
        "planner_output": planner_output,
        "missing_fields": [],
    }


async def invoice_node(state: PlannerAppState) -> dict:
    client = InvoiceA2AClient()
    planner_output = state["planner_output"]

    invoice_task = next(
        task for task in planner_output["tasks"]
        if task["agent"] == "invoice"
    )

    instruction = build_instruction_from_task(invoice_task)
    result = await client.ask(invoice_task["instruction"])

    return {
        "invoice_result": result,
    }


async def music_node(state: PlannerAppState) -> dict:
    client = MusicA2AClient()
    planner_output = state["planner_output"]

    music_task = next(
        task for task in planner_output["tasks"]
        if task["agent"] == "music"
    )

    instruction = build_instruction_from_task(music_task)
    result = await client.ask(music_task["instruction"])

    return {
        "music_result": result,
    }


def final_response_node(state: PlannerAppState) -> dict:
    invoice_result = state.get("invoice_result")
    music_result = state.get("music_result")

    results: list[AgentResult] = []

    if invoice_result:
        results.append(
            AgentResult(
                agent="invoice",
                result=invoice_result,
            )
        )

    if music_result:
        results.append(
            AgentResult(
                agent="music",
                result=music_result,
            )
        )

    if not results:
        planner_output = state.get("planner_output", {})
        tasks = planner_output.get("tasks", [])

        if not tasks:
            return {
                "final_answer": (
                    "I can help with invoice and music tasks.\n\n"
                    "Examples:\n"
                    "- Get latest invoice for customer_id=5\n"
                    "- Show invoices sorted by unit price for customer_id=5\n"
                    "- Find tracks by artist AC/DC\n"
                    "- Recommend songs by genre rock\n"
                    "- Check for song Ligia\n\n"
                    "For vague music requests like 'recommend some songs', "
                    "I will ask whether you want to search by artist or by genre."
                )
            }

        return {
            "final_answer": "I could not complete the request."
        }

    output = aggregator.invoke(
        AggregatorInput(
            user_input=state["user_input"],
            results=results,
        )
    )

    return {
        "final_answer": output.final_answer
    }
