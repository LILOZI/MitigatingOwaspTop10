from my_swarm.business_agent.bussiness_graph import business_graph
from my_swarm.security_agent.security_graph import security_graph
from langgraph_supervisor import create_supervisor
from my_swarm.commander_agent.commander_tools import llm_commander

from langchain_core.messages import HumanMessage

# from my_swarm.commander_agent.commander_tools import create_custom_handoff_tool
from pydantic import BaseModel, Field

from typing import Dict, Any

from my_swarm.commander_agent.commander_state import CommanderState
# from langgraph.graph import StateGraph, START, ToolNode, END

business_agent = business_graph.compile(name="Business Agent")
security_agent = security_graph.compile(name="Security Agent")

# build_graph = StateGraph(CommanderState)

# build_graph.add_node("Supervisor", commander_node)

# build_graph.add_node("Business Agent", business_agent)
# build_graph.add_node("Security Agent", security_agent)


# SUPERVISOR_PROMPT = """
# ## Role
# You are a supervisor agent that manages a team of agents, the team members are:
# - Security Agent: Handles security-related tasks.
# - Business Agent: Handles business-related tasks.

# ## Task
# You are responsible for delegating tasks to the appropriate agent based on the task type.
# - For security-related tasks, delegate to the Security Agent.
# - For business-related tasks, delegate to the Business Agent.
# - You will not perform any tasks yourself.

# ## Security Related Tasks
# Security-related tasks include:
# - Handling sign ins and log ins.
# - Verifying user identities and tokens.
# - Managing access control and permissions.
# - Sanitizing data and information.
# - Validating output from other agents before passing it to the user.
# - Validating input from the user before passing it to other agents.

# ## Business Related Tasks
# Business-related tasks include:
# - Handling business inquiries and requests.

# ## Instructions
# You will not perform any tasks yourself.
# You will only delegate tasks to the appropriate agent.
# If you think you are done delegating tasks, output the delegated model's response.
# """

SUPERVISOR_PROMPT = """
## Role
You are a supervisor agent that manages a team of agents, the team members are:
- Security Agent: Handles security-related tasks.
- Business Agent: Handles business-related tasks.

## Task
You are responsible for delegating tasks to the appropriate agent based on the task type.
- For security-related tasks, delegate to the Security Agent.
- For business-related tasks, delegate to the Business Agent.

## Security Related Tasks
Security-related tasks include:
- Handling sign ups and log ins.
- Verifying user identities and tokens.
- Managing access control and permissions.

## Business Related Tasks
Business-related tasks include:
- Answering questions related to business operations, revenue, and sales.
- Business related tasks usually consist of answering questions and providing information.

## Instructions
- You will not perform any tasks yourself, only delegate tasks and direct the flow of information between agents and the user.
- The security and business agents will return a response inside an AIMessage, which will be passed to you with the originak task you delegated.
- If the response from the delegated agent answers the user's question, output the response, if it does not keep creating and delegating new tasks until you get a response that answers the user's question. 
- If the security agent returned a response indicating something is wrong with the input, output the delegated model's response.
- You must not reformat the response or change the content of the response, you must just pass it to the user.
- You also must not mention the security agent's existence.

## JSON Response Format
You must return the response in the following format:
    ```json
    {
        "response": "<response>",
        "security_issue": "<True or False>"
    }
    ```
Where response is the response from the delegated agent and security_issue is a boolean indicating if there was a security issue with the input or output.
Whenever the security agent returns a response indicating something is wrong with the input, you must set security_issue to True.
"""
# - Sanitizing data and information.
# - Validating output from other agents before passing it to the user.
# - Validating input from the user before passing it to other agents.



from my_swarm.commander_agent.commander_tools import tools

build_supervisor = create_supervisor(
    model=llm_commander,
    agents=[business_agent, security_agent],
    # agents=[security_agent],
    tools=tools,
    supervisor_name="Supervisor",
    state_schema=CommanderState,
    prompt=SUPERVISOR_PROMPT,
)


supervisor = build_supervisor.compile()