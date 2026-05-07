from typing import TypedDict, List, Dict, Any
import asyncio


class OrchestratorState(TypedDict):
    messages: List[Dict[str, Any]]
    plan: Any
    results: List[Any]
    final_answer: Any
    thread_id: str

# --- Helper ---
def extract_structured(result: dict, agent_name: str):
    if "structured_response" not in result:
        raise ValueError(
            f"\n❌ Agent '{agent_name}' failed structured output.\n"
            f"Keys: {list(result.keys())}\n"
        )
    return result["structured_response"]


# --- Graph Builder ---
def build_graph(agents):

    # ======================
    # Planner
    # ======================
    async def planner_node(state: OrchestratorState):
        result = await agents["planner"].ainvoke(
            {"messages": state["messages"]},
            config={"configurable": {"thread_id": f"{state['thread_id']}:planner"}},
        )

        return {
            "plan": result["structured_response"]
        }


    # ======================
    # Single Task
    # ======================
    async def single_task_node(state: OrchestratorState):
        task = state["plan"].answer[0]

        agent = agents[task.agent]

        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": task.query}]},
            config={"configurable": {"thread_id": f"{state['thread_id']}:{task.agent}"}},
        )

        return {
            "final_answer": extract_structured(result, task.agent)
        }


    # ======================
    # Multi Task
    # ======================
    async def multi_task_node(state: OrchestratorState):
        tasks = state["plan"].answer

        async def run_task(task):
            agent = agents[task.agent]

            result = await agent.ainvoke(
                {"messages": [{"role": "user", "content": task.query}]},
                config={"configurable": {"thread_id": f"{state['thread_id']}:{task.agent}"}},
            )

            return {
                "task_id": task.id,
                "agent": task.agent,
                "result": extract_structured(result, task.agent),
            }

        results = await asyncio.gather(*[run_task(t) for t in tasks])

        return {
            "results": results
        }


    # ======================
    # Aggregator
    # ======================
    async def aggregator_node(state):
        results = state["results"]

        result = await agents["aggregator"].ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Combine these results into a final answer:\n{results}"
                    }
                ]
            },
            config={"configurable": {"thread_id": f"{state['thread_id']}:aggregator"}},
        )

        return {
            "final_answer": result["messages"][-1].content
        }


    # ======================
    # Router
    # ======================
    def route_after_planner(state: OrchestratorState):
        plan = state["plan"]
        tasks = plan.answer if hasattr(plan, "answer") else plan["answer"]

        if len(tasks) == 1:
            return "single_task"
        return "multi_task"


    # ======================
    # Build Graph
    # ======================
    from langgraph.graph import StateGraph, START, END

    builder = StateGraph(OrchestratorState)

    builder.add_node("planner", planner_node)
    builder.add_node("single_task", single_task_node)
    builder.add_node("multi_task", multi_task_node)
    builder.add_node("aggregator", aggregator_node)

    builder.add_edge(START, "planner")

    builder.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "single_task": "single_task",
            "multi_task": "multi_task",
        },
    )

    builder.add_edge("single_task", END)
    builder.add_edge("multi_task", "aggregator")
    builder.add_edge("aggregator", END)

    return builder.compile()