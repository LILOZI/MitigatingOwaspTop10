from langgraph.graph import MessagesState

from langgraph.types import Command, Send

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from typing import Literal

from langchain_ollama import ChatOllama

from langgraph_swarm import create_handoff_tool, create_swarm

transfer_security = create_handoff_tool(agent_name="Security Agent",
                    description="Transfer the user to the Security Agent",)

transfer_business = create_handoff_tool(agent_name="Business Agent",
                    description="Transfer the user to the Business Agent",)

llm_commander = ChatOllama(model="llama3.2:3b").bind_tools(
    [transfer_security, transfer_business])


def commander_node(state: MessagesState):
    """
    This function is an agent that decides what to do based on the state of the conversation.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    print("Commander Agent")
    pass


def commander_respond(state: MessagesState):
    """
    This function is an agent that decides what to do based on the state of the conversation.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    print("Commander Respond")
    pass