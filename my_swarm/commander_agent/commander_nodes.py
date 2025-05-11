from my_swarm.commander_agent.commander_state import CommanderState

from langgraph.types import Command, Send

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

# from typing import Literal

from my_swarm.commander_agent.commander_tools import llm_commander

from my_swarm.commander_agent.prompts import (
    SYSTEM_MESSAGE_LEBRON,
)

def commander_node(state: CommanderState):
    """
    This function is an agent that decides what to do based on the state of the conversation.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    print(f"Commander Node: {state}")
    if type(state["messages"][-1]) == ToolMessage and state["messages"][-1].tool_call_id == "2":
        pass
    sys_msg = SystemMessage(content=SYSTEM_MESSAGE_LEBRON)
    msgs = state["messages"]
    state_update = {}
    state_update["messages"] = []
    auth_token = state.get("auth_token")
    
    if not state.get("is_authenticated", False) and (auth_token is not None and auth_token != ""):
        msg = HumanMessage(content=f"Verify token={auth_token} for user={state['username']}")
        msgs.append(msg)
        state_update["messages"] += [msg]
    commander_response = llm_commander.invoke([sys_msg] + msgs)
    state_update["messages"] += [commander_response]
    print(f"Commander Agent Response: {commander_response}")
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

