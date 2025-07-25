from langgraph.graph import StateGraph, START, END

from langgraph.prebuilt import ToolNode

from my_swarm.business_agent.business_state import BusinessState
from my_swarm.business_agent.business_nodes import (
    business_node,
    business_tool_choice,
    business_respond_helper,
)

from my_swarm.business_agent.business_tools import (
    lebron_body_retreiver,
    lebron_intro_retreiver,
)

business_graph = StateGraph(BusinessState)

business_graph.add_node("Business Agent", business_node)

business_graph.add_edge(START, "Business Agent")

business_graph.add_node(
    "Retriever",
    ToolNode(
        tools=[lebron_body_retreiver, lebron_intro_retreiver],
    )
)

business_graph.add_node("Respond", business_respond_helper)

business_graph.add_conditional_edges(
    "Business Agent",
    business_tool_choice,
    {
        "Retriever": "Retriever",
        # "Schema Generator": "Schema Generator",
        "Respond": "Respond",
        "Business Agent": "Business Agent",
    },
)

business_graph.add_edge("Retriever", "Business Agent")
