from langgraph.graph import StateGraph, START, END

from my_swarm.security_agent.security_state import SecurityState

from my_swarm.security_agent.security_nodes import (
    security_node,
    security_respond,
    security_tool_choice,
)

from my_swarm.security_agent.security_tools import (
    security_retriever,
    security_sanitizer,   
)


security_graph = StateGraph(SecurityState)

security_graph.add_node("Security Agent", security_node)
security_graph.add_node("Retriever", security_retriever)
security_graph.add_node("Sanitizer", security_sanitizer)
security_graph.add_node("Respond", security_respond)

security_graph.add_edge(START, "Security Agent")
security_graph.add_conditional_edges(
    "Security Agent", security_tool_choice,
    {
        "Sanitizer": "Sanitizer",
        "Retriever": "Retriever",
        "Respond": "Respond",
    },
)

security_graph.add_edge("Sanitizer", "Security Agent")
security_graph.add_edge("Retriever", "Security Agent")
security_graph.add_edge("Respond", "Security Agent")
