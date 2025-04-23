# from my_swarm.commander_agent.commander_state import CommanderState

# from langgraph.types import Command, Send

# from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# from typing import Literal

# from my_swarm.commander_agent.commander_tools import llm_commander


# def commander_node(state: CommanderState) -> Command:
#     """
#     This function is an agent that decides what to do based on the state of the conversation.
#     It can either respond to the user, ask for more information, or exit the conversation.
#     """
#     sys_msg = SystemMessage("You are the Commander Agent. You can transfer to Security or Business Agent."
#                             "\nThe security agent is responsible for security-related tasks, such as user authentication.")
#     commander_response = llm_commander.invoke([sys_msg, HumanMessage(state["messages"][-1].content)])
#     return {"messages": commander_response}

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