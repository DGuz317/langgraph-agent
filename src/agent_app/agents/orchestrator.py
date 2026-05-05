import uuid
import asyncio
from typing import Any, TypedDict

from langgraph.graph import StateGraph, START, END


class OrchestratorState(TypedDict):
    messages: list
    plan: dict
    results: list
    final_answer: Any
    thread_id: str


def extract_structured(result: dict, task_agent: str):
    """
    Safely pull structured_response out of an agent's ainvoke return value.
    Raises a clear error if the key is missing (helps diagnose missing
    response_format on a sub-agent).
    """
    if "structured_response" not in result:
        available_keys = list(result.keys())
        raise ValueError(
            f"Agent '{task_agent}' did not return 'structured_response'. "
            f"Available keys: {available_keys}. "
            f"Make sure response_format is set on this agent."
        )
    return result["structured_response"]


def get_planner():
    from agent_app.agents.planner_agent import planner_agent
    return planner_agent

def get_agents():
    from agent_app.agents.invoice_agent import invoice_agent
    from agent_app.agents.music_agent import music_agent
    return {
        "invoice_agent": invoice_agent,
        "music_agent": music_agent,
    }


async def planner_node(state: OrchestratorState):
    result = await get_planner().ainvoke(
        {"messages": state["messages"]},
        config={"configurable": {"thread_id": state["thread_id"]}},
    )
    return {"plan": result["structured_response"]}


async def single_task_node(state: OrchestratorState):
    agents = get_agents()
    task = state["plan"].answer[0]
    agent = agents[task.agent]

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": task.query}]},
        config={"configurable": {"thread_id": state["thread_id"]}},
    )

    structured = extract_structured(result, task.agent)
    if structured.status == "input_required":
        return {
            "plan": {**state["plan"].model_dump(), "status": "input_required",
                     "clarification_message": structured.answer},
            "final_answer": None,
        }
 
    return {"final_answer": structured}


async def multi_task_node(state: OrchestratorState):
    agents = get_agents()
    tasks = state["plan"].answer
 
    async def run_task(task):
        agent = agents[task.agent]
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": task.query}]},
            config={"configurable": {"thread_id": state["thread_id"]}},
        )
        return extract_structured(result, task.agent)

    structured_results = await asyncio.gather(*[run_task(t) for t in tasks])

    missing = [
        r.answer for r in structured_results
        if r.status == "input_required"
    ]
    if missing:
        clarification = " | ".join(filter(None, missing))
        return {
            "plan": {**state["plan"].model_dump(), "status": "input_required",
                     "clarification_message": clarification},
            "results": [],
        }
 
    return {"results": structured_results}


def aggregator_node(state: OrchestratorState):
    tasks = state["plan"].answer
    results = state["results"]
    return {
        "final_answer": [
            {
                "task_id": task.id,
                "agent": task.agent,
                "result": r,
            }
            for task, r in zip(tasks, results)
        ]
    }


async def ask_user_node(state: OrchestratorState):
    clarification = state["plan"].get(
        "clarification_message", 
        "Could you provide more details so I can proceed?"
        )
    return {"final_answer": clarification}


def route_after_planner(state: OrchestratorState):
    plan = state["plan"]
 
    if plan.status == "input_required":
        return "ask_user"
 
    if len(plan.answer) > 1 and plan.requires_aggregation:
        return "multi_task"

    return "single_task"


def route_after_task(state: OrchestratorState):
    plan = state["plan"]
    status = plan.get("status") if isinstance(plan, dict) else plan.status
    if status == "input_required":
        return "ask_user"
    return "continue"


builder = StateGraph(OrchestratorState)

builder.add_node("planner", planner_node)
builder.add_node("single_task", single_task_node)
builder.add_node("multi_task", multi_task_node)
builder.add_node("aggregator", aggregator_node)
builder.add_node("ask_user", ask_user_node)

builder.add_edge(START, "planner")

builder.add_conditional_edges(
    "planner",
    route_after_planner,
    {
        "single_task": "single_task",
        "multi_task": "multi_task",
        "ask_user": "ask_user",
    },
)

builder.add_conditional_edges(
    "single_task",
    route_after_task,
    {
        "ask_user": "ask_user",
        "continue": END,
    },
)

builder.add_conditional_edges(
    "multi_task",
    route_after_task,
    {
        "ask_user": "ask_user",
        "continue": "aggregator",
    },
)

builder.add_edge("aggregator", END)
builder.add_edge("ask_user", END)

graph = builder.compile()


async def run_session(user_message: str, history: list = None, thread_id: str = None):
    thread_id = thread_id or str(uuid.uuid4())
    messages = (history or []) + [{"role": "user", "content": user_message}]
 
    result = await graph.ainvoke(
        {
            "messages": messages,
            "thread_id": thread_id,
            "plan": {},
            "results": [],
            "final_answer": None,
        }
    )
    return result
