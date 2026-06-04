from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver

from multi_agent_system.planner_app.edges import (
    route_after_invoice,
    route_after_planner,
)
from multi_agent_system.planner_app.nodes import (
    final_response_node,
    invoice_node,
    music_node,
    planner_node,
)
from multi_agent_system.planner_app.state import PlannerAppState

PLANNER_GRAPH_NAME = "planner.workflow"


def build_graph(checkpointer: Any | None = None):
    graph = StateGraph(PlannerAppState)

    graph.add_node("planner", planner_node)
    graph.add_node("invoice", invoice_node)
    graph.add_node("music", music_node)
    graph.add_node("final_response", final_response_node)

    graph.add_edge(START, "planner")

    graph.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "invoice": "invoice",
            "music": "music",
            "final_response": "final_response",
        },
    )

    graph.add_conditional_edges(
        "invoice",
        route_after_invoice,
        {
            "music": "music",
            "final_response": "final_response",
        },
    )

    graph.add_edge("music", "final_response")
    graph.add_edge("final_response", END)


    return graph.compile(
        checkpointer=checkpointer or InMemorySaver(),
        name=PLANNER_GRAPH_NAME,
    )


planner_graph = build_graph()
