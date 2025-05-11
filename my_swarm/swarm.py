from my_swarm.commander_agent.commander_graph import commander_graph

from langgraph.checkpoint.memory import InMemorySaver

memory_saver = InMemorySaver()

supervisor = commander_graph.compile(checkpointer=memory_saver)