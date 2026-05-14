from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient
from multi_agent_system.a2a_client.music_client import MusicA2AClient
from multi_agent_system.planner.agent import PlannerAgent
from multi_agent_system.planner_app.state import PlannerAppState
from multi_agent_system.planner_app.hitl import interrupt_for_missing_info
from multi_agent_system.aggregator.agent import AggregatorAgent
from multi_agent_system.aggregator.schemas import AggregatorInput, AgentResult


planner = PlannerAgent(
    use_llm=True,
    fallback_to_deterministic=False,
)
aggregator = AggregatorAgent()


def _build_hitl_planner_input(user_input: str, extracted: dict) -> str:
    details = [
        f"{field}={value}"
        for field, value in sorted(extracted.items())
        if value not in (None, "")
    ]

    if not details:
        return user_input

    return (
        f"{user_input}\n\n"
        "Additional information collected from the user: "
        f"{', '.join(details)}"
    )


def planner_node(state: PlannerAppState) -> dict:
    output = planner.invoke(state["user_input"])

    return {
        "planner_output": output.model_dump(),
        "missing_fields": output.missing_fields,
    }


def missing_info_node(state: PlannerAppState) -> dict:
    missing_fields = state.get("missing_fields", [])
    extracted = interrupt_for_missing_info(missing_fields)

    planner_input = _build_hitl_planner_input(state["user_input"], extracted)
    output = planner.invoke(planner_input)

    return {
        **extracted,
        "planner_output": output.model_dump(),
        "missing_fields": output.missing_fields,
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
