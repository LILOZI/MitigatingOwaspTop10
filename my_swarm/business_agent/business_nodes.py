from my_swarm.business_agent.business_state import BusinessState

from langgraph.types import Command, Send

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage

from typing import Literal

from my_swarm.business_agent.business_tools import llm_business

from my_swarm.business_agent.prompts import (
    SYSTEM_MESSAGE_LEBRON,
)

def business_node(state: BusinessState):
    """
    This function is an agent that handles business-related tasks.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    print(f"Business Node: {state}")
    sys_msg = SystemMessage(
        content=SYSTEM_MESSAGE_LEBRON,
    )
    response = llm_business.invoke([sys_msg] + state["messages"])
    if response.tool_calls is None or len(response.tool_calls) == 0:
        response = HumanMessage(content=response.content, )
    print(f"Business Agent Response: {response.content}")
    return {"messages": [response]}


name_to_tool = {
    "lebron_info_retriever": "Retriever",
    "lebron_body_retreiver": "Retriever",
    "business_respond": "Respond",
}

def business_tool_choice(state: BusinessState) -> Literal["Sanitizer", "Retrieveer",
    "Respond", "Business Agent"]:
    """
    This function chooses the appropriate tool for business-related tasks.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    tool_choice = ""
    if type(state["messages"][-1]) is AIMessage:
        if state["messages"][-1].tool_calls is not None and len(state["messages"][-1].tool_calls) > 0:
            tool_choice = state["messages"][-1].tool_calls[0]["name"]
    return name_to_tool.get(tool_choice, "Business Agent")
        

def business_respond_helper(state: BusinessState):
    """
    Format and return the response that the business agent created.
    Args:
        response (str): The response to be returned.
    """
    print("Business Agent Responding...")
    
    response = state["messages"][-2].content
    state_update = {
                "messages": [state["messages"][0],
                    HumanMessage(
                    content=f"**Business Agent** response: COPY THE CONTENT WITHIN THE <START> <END> TAGS "\
                        f"EXACTLY WITHOUT ANY CHANGES AND HAVE THE SECURITY AGENT VALIDATE IT <START>{response}<END>",
                ),
                ToolMessage(
                    content=f"**Business Agent** Handoff → **Supervisor**",
                    name="handoff_to_supervisor",
                    tool_call_id="2",
                )],
            }
    return Command(
                goto=Send("Supervisor", arg=state_update),
                update=state_update,
                graph=Command.PARENT
            )