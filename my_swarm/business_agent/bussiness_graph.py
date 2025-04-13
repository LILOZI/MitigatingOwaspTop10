from langgraph.graph import StateGraph, START

from my_swarm.business_agent.business_state import BusinessState
from my_swarm.business_agent.business_nodes import (
    business_node,
    business_tool_choice,
    bussiness_respond,
)

from my_swarm.business_agent.business_tools import (
    business_retreiver,
    business_schema_generator,
)


business_graph = StateGraph(BusinessState)

business_graph.add_node("Business Agent", business_node)
business_graph.add_node("Retriever", business_retreiver)
business_graph.add_node("Schema Generator", business_schema_generator)

business_graph.add_edge(START, "Business Agent")
business_graph.add_conditional_edges(
    "Business Agent", business_tool_choice,
    {
        "Retriever": "Retriever",
        "Schema Generator": "Schema Generator",
    },
)

business_graph.add_edge("Retriever", "Business Agent")
business_graph.add_edge("Schema Generator", "Business Agent")
