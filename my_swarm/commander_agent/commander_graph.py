from langgraph.graph import StateGraph, START

from langgraph.prebuilt import ToolNode, tools_condition

from my_swarm.commander_agent.commander_state import CommanderState

from my_swarm.commander_agent.commander_nodes import (
    commander_node,
)

from my_swarm.commander_agent.commander_tools import (
    tools,
)

from my_swarm.security_agent.security_graph import security_graph
from my_swarm.business_agent.bussiness_graph import business_graph

business_agent = business_graph.compile(name="Business Agent")
security_agent = security_graph.compile(name="Security Agent")

commander_graph = StateGraph(CommanderState)

commander_graph.add_node("Supervisor", commander_node)

commander_graph.add_edge(START, "Supervisor")

commander_graph.add_node("tools", ToolNode(tools))

commander_graph.add_edge("tools", "Supervisor")

commander_graph.add_conditional_edges("Supervisor", tools_condition)

commander_graph.add_node("Security Agent", security_agent)

commander_graph.add_node("Business Agent", business_agent)


