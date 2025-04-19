from my_swarm.commander_agent.commander_graph import commander_graph, comader_memory
from my_swarm.business_agent.bussiness_graph import business_graph
from my_swarm.security_agent.security_graph import security_graph
from langgraph_swarm import create_swarm



commander_agent = commander_graph.compile(name="Commander Agent", memory=comader_memory)
business_agent = business_graph.compile(name="Business Agent")
security_agent = security_graph.compile(name="Security Agent")

build_swarm = create_swarm([commander_agent, business_agent, security_agent], 
                    default_active_agent="Commander Agent")

swarm = build_swarm.compile()