from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver

from multi_agent_system.planner_app.edges import (
    route_after_invoice,
    route_after_planner,
)
from multi_agent_system.planner_app.nodes import (
    final_response_node,
    invoice_node,
    missing_info_node,
    music_node,
    planner_node,
)
from multi_agent_system.planner_app.state import PlannerAppState


def build_graph():
    graph = StateGraph(PlannerAppState)

    graph.add_node("planner", planner_node)
    graph.add_node("missing_info", missing_info_node)
    graph.add_node("invoice", invoice_node)
    graph.add_node("music", music_node)
    graph.add_node("final_response", final_response_node)

    graph.add_edge(START, "planner")

    graph.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "missing_info": "missing_info",
            "invoice": "invoice",
            "music": "music",
            "final_response": "final_response",
        },
    )

    graph.add_conditional_edges(
        "missing_info",
        route_after_planner,
        {
            "missing_info": "missing_info",
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


    checkpointer = InMemorySaver()
    return graph.compile(checkpointer=checkpointer)


planner_graph = build_graph()