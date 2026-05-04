from agent_app.agents import invoice_agent, music_agent, planner_agent

from langgraph.graph import StateGraph, START, END

class OrchestratorState(TypedDict):

    pass


AGENTS = {
    "invoice_agent": invoice_agent,
    "music_agent": music_agent,
}

async def single_task_node(state):
    task = state["plan"]["answer"][0]

    agent = AGENTS[task["agent"]]

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": task["query"]}]},
        config={"configurable": {"thread_id": "1"}},
    )

    return {
        "final_answer": result["structured_response"]
    }

async def multi_task_node(state):
    tasks = state["plan"]["answer"]

    async def run_task(task):
        agent = AGENTS[task["agent"]]
        return await agent.ainvoke(
            {"messages": [{"role": "user", "content": task["query"]}]},
            config={"configurable": {"thread_id": "1"}},
        )

    results = await asyncio.gather(*[run_task(t) for t in tasks])

    return {
        "results": [r["structured_response"] for r in results]
    }

def route_after_planner(state):
    plan = state["plan"]
    tasks = plan["answer"]

    if plan["status"] == "input_required":
        return "ask_user"

    elif len(tasks) > 1 and plan["requires_aggregation"]:
        return "multi_task_with_aggregation"
    else:
        return "single_task"

def aggregator_node(state):
    return {
    "results": [
        {
            "task_id": task["id"],
            "agent": task["agent"],
            "result": r["structured_response"]
        }
        for task, r in zip(tasks, results)
    ]
}

workflow = (
    StateGraph(State)
    .add_node("agent", agent_node)
    .add_node("agent", agent_node)
    .add_node("agent", agent_node)
    .add_edge(START, "agent")
    .add_edge("agent", END)
    .compile()
)