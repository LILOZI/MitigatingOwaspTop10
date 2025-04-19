from langgraph.graph import StateGraph, START

from my_swarm.commander_agent.commander_state import CommanderState

from my_swarm.commander_agent.commander_nodes import (
    commander_node,
)

from langgraph.checkpoint.memory import MemorySaver

comader_memory = MemorySaver()

commander_graph = StateGraph(CommanderState)

commander_graph.add_node("Commander Agent", commander_node)
commander_graph.add_edge(START, "Commander Agent")


