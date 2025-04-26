from my_swarm.commander_agent.commander_state import CommanderState

from langgraph.types import Command, Send

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# from typing import Literal

from my_swarm.commander_agent.commander_tools import llm_commander


def commander_node(state: CommanderState):
    """
    This function is an agent that decides what to do based on the state of the conversation.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    print(f"Commander Node: {state}")
    sys_msg = SystemMessage(content=SUPERVISOR_PROMPT)
    msgs = state["messages"]
    state_update = {}
    state_update["messages"] = []
    auth_token = state.get("auth_token")
    if not state.get("is_authenticated", False) and (auth_token is not None and auth_token != ""):
        msg = HumanMessage(content=f"Verify token={auth_token} for user={state['username']}")
        msgs.append(msg)
        state_update["messages"] += [msg]
    commander_response = llm_commander.invoke([sys_msg] + msgs)
    print(f"Commander Agent Response: {commander_response}")
    state_update["messages"] += [commander_response]
    return state_update

# def execute_command(state: CommanderState) -> Command:
#     if state["messages"][-1].tool_calls is not None:
#         tool_choice = state["messages"][-1].tool_calls[0]["name"]
#         return Command(goto=tool_choice, update={"username": state["messages"][-1].tool_calls[0]["args"]["username"]})
#     pass

# def commander_respond(state: CommanderState) -> Command:
#     """
#     This function is an agent that decides what to do based on the state of the conversation.
#     It can either respond to the user, ask for more information, or exit the conversation.
#     """
#     print("Commander Respond")
#     pass

# def commander_tool_choice(state: CommanderState) -> Literal["Business Agent",
#     "Security Agent", "Commander Agent"]:
#     """
#     This function decides which agent to transfer the conversation to based on the state of the conversation.
#     """
#     if type(state["messages"][-1]) is AIMessage:
#         if state["messages"][-1].tool_calls is not None:
#             tool_choice = state["messages"][-1].tool_calls[0]["name"]
#             return tool_choice
#     else:
#         return "Commander Agent"

SUPERVISOR_PROMPT = """
## Role
You are a supervisor agent that manages a team of agents, the team members are:
- Security Agent: Handles security-related tasks.
- Business Agent: Handles business-related tasks.

## Task
You are responsible for delegating tasks to the appropriate agent based on the task type.
- For security-related tasks, delegate to the Security Agent.
- For business-related tasks, delegate to the Business Agent.

## Instructions
- You will not perform any tasks yourself, only delegate tasks and direct the flow of information between agents and the user.
- The security and business agents will return a response inside an HumanMessage, which will be passed to you with the originak task you delegated.
- If the response from the delegated agent answers the user's question, output the response, if it does not keep creating and delegating new tasks until you get a response that answers the user's question. 
- If the security agent returned a response indicating something is wrong with the input, output the delegated model's response.
- You must not reformat the response or change the content of the response, you must just pass it to the user.
- You also must not mention the security agent's existence.
- Do not delegate tasks to the business agent if no question was asked, business related tasks are only to answer questions and provide information.

## Security Related Tasks
Security-related tasks include:
- Handling sign ups and log ins.
- Verifying user's tokens.
- Managing access control and permissions.

## Business Related Tasks
Business-related tasks include:
- Answering questions related to business operations, revenue, and sales.
- Business related tasks usually consist of answering questions and providing information.
Businees-related tasks do not include:
- Access control and permissions.
- User authentication and identity verification.
- Handling sign ups and log ins.

## JSON Response Format
You must return the response in the following JSON format:

{
    "response": "<response>",
    "security_issue": "<True or False>"
}

Where response is the response from the delegated agent and security_issue is a boolean indicating if there was a security issue with the input or output.
Whenever the security agent returns a response indicating an error with the input, you must set security_issue to True.
"""