import re

from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient
from multi_agent_system.a2a_client.music_client import MusicA2AClient
from multi_agent_system.planner.agent import PlannerAgent
from multi_agent_system.planner_app.state import PlannerAppState
from multi_agent_system.planner_app.hitl import interrupt_for_missing_info
from multi_agent_system.aggregator.agent import AggregatorAgent
from multi_agent_system.aggregator.schemas import AggregatorInput, AgentResult


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
            intent = task.get("intent")

            if intent == "invoices_by_unit_price":
                task["instruction"] = (
                    f"Get invoices sorted by unit price for customer_id={customer_id}"
                )
            else:
                task["intent"] = "latest_invoice"
                task["instruction"] = f"Get latest invoice for customer_id={customer_id}"

            task["missing_fields"] = []
            _update_task_args(task, {"customer_id": customer_id})

        if task["agent"] == "music" and extracted.get("artist"):
            artist = extracted["artist"]

            task["intent"] = "tracks_by_artist"
            task["instruction"] = f"Find tracks by artist {artist}"
            task["missing_fields"] = []
            _update_task_args(task, {"artist": artist})

        if task["agent"] == "music" and extracted.get("genre"):
            genre = extracted["genre"]

            task["intent"] = "songs_by_genre"
            task["instruction"] = f"Recommend songs by genre {genre}"
            task["missing_fields"] = []
            _update_task_args(task, {"genre": genre})

        if task["agent"] == "music" and extracted.get("song_title"):
            song_title = extracted["song_title"]

            task["intent"] = "check_song"
            task["instruction"] = f"Check for song {song_title}"
            task["missing_fields"] = []
            _update_task_args(task, {"song_title": song_title})

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
