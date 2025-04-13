from langgraph.graph import MessagesState

from langgraph.types import Command, Send

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from typing import Literal

from langchain_ollama import ChatOllama

from langgraph_swarm import create_handoff_tool, create_swarm


transfer_security = create_handoff_tool(agent_name="Security Agent",
                    description="Transfer the user to the Security Agent",)

transfer_commander = create_handoff_tool(agent_name="Commander Agent",
                    description="Transfer the user to the Commander Agent",)


llm_business = ChatOllama(model="llama3.2:3b").bind_tools(
    [transfer_security, transfer_commander])


def business_node(state: MessagesState):
    """
    This function is an agent that handles business-related tasks.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    print("Business Agent")
    pass


def bussiness_respond(state: MessagesState):
    """
    This function is an agent that handles business-related tasks.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    print("Business Agent Responding...")
    # return Command(
    #     update={"messages": AIMessage("Business Agent Responding")},
    #     goto=Send("Business Agent", None)
    # )
    pass

def business_tool_choice(state: MessagesState) -> Literal["Sanitizer", "Retriever", "Respond"]:
    """
    This function chooses the appropriate tool for business-related tasks.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    pass