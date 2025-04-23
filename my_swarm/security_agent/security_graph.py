from langgraph.graph import StateGraph, START, END

from langgraph.prebuilt import ToolNode

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

from my_swarm.security_agent.access_control import (
    execute_access_control,
    access_control_tools,
)

security_graph = StateGraph(SecurityState)

security_graph.add_node("Security Agent", security_node)
security_graph.add_node("Retriever", security_retriever)
security_graph.add_node("Sanitizer", security_sanitizer)
security_graph.add_node("Respond", security_respond)

# security_graph.add_node("Access Control", execute_access_control)
security_graph.add_node("Access Control", execute_access_control)

security_graph.add_edge(START, "Security Agent")
# security_graph.add_conditional_edges(
#     "Security Agent", security_tool_choice,
#     {
#         "Security Agent": "Security Agent",
#         "Access Control": "Access Control",
#         "Sanitizer": "Sanitizer",
#         "Retriever": "Retriever",
#         "Respond": "Respond",
#     },
# )
security_graph.add_node("tool_choice", security_tool_choice)
security_graph.add_edge("Security Agent", "tool_choice")

# security_graph.add_edge("Sanitizer", "Security Agent")
# security_graph.add_edge("Retriever", "Security Agent")
# security_graph.add_edge("Access Control", "Respond")
# security_graph.add_edge("Respond", END)

