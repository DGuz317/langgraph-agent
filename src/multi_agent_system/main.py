from langgraph.graph import StateGraph, START, END

from my_agent.utils.state import AppState
from my_agent.utils.routing import should_aggregate
from my_agent.utils.constants import (
    AGGREGATE_NODE,
    EXECUTE_TASKS_NODE,
    PLANNER_NODE
)
from my_agent.utils.nodes import (
    planner_node,
    execute_tasks_node,
    aggregate_node,
)

def build_graph():
    builder = StateGraph(AppState)

    builder.add_node(PLANNER_NODE, planner_node)
    builder.add_node(EXECUTE_TASKS_NODE, execute_tasks_node)
    builder.add_node(AGGREGATE_NODE, aggregate_node)

    builder.add_edge(START, PLANNER_NODE)
    builder.add_edge(PLANNER_NODE, EXECUTE_TASKS_NODE)

    builder.add_conditional_edges(
        EXECUTE_TASKS_NODE,
        should_aggregate,
        {
            "aggregate": AGGREGATE_NODE,
            "end": END
        }
    )

    builder.add_edge(AGGREGATE_NODE, END)

    return builder.compile()


graph = build_graph()