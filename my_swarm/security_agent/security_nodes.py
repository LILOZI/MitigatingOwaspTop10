from langgraph.graph import MessagesState

from langgraph.types import Command, Send

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from typing import Literal

from langchain_ollama import ChatOllama

from langgraph_swarm import create_handoff_tool, create_swarm


transfer_commander = create_handoff_tool(agent_name="Commander Agent",
                    description="Transfer the user to the Commander Agent",)

transfer_business = create_handoff_tool(agent_name="Business Agent",
                    description="Transfer the user to the Business Agent",)

llm_security = ChatOllama(model="llama3.2:3b")


def security_node(state: MessagesState):
    """
    This function is an agent that handles security-related tasks.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    print("Security Agent")
    pass

def security_tool_choice(state: MessagesState) -> Literal["Sanitizer", "Retriever", "Respond"]:
    """
    This function chooses the appropriate tool for security-related tasks.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    pass

def security_respond(state: MessagesState):
    """
    This function is an agent that handles security-related tasks.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    print("Security Agent Responding...")
    # return Command(
    #     update={"messages": AIMessage("Security Agent Responding")},
    #     goto=Send("Security Agent", None)
    # )
    pass