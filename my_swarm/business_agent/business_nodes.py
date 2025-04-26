from my_swarm.business_agent.business_state import BusinessState

from langgraph.types import Command, Send

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage

from typing import Literal

from my_swarm.business_agent.business_tools import llm_business

def business_node(state: BusinessState):
    """
    This function is an agent that handles business-related tasks.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    print(f"Business Node: {state}")
    sys_msg = SystemMessage(
        content="You are a business agent that answers business-related questions. "
                "Given the user input, decide which business tool to use.\n"
                "You can use tools to retreive information or answer by yourself. "
                "The retreived information and your previous answers and reasoning will be given to you as input for context, along with the question itself.\n"
                "The questions will be given first, after it will be your steps, when you see that the information after question "
                "answers it, finish by calling the business_respond tool to return the answer.\n"
    )
    response = llm_business.invoke([sys_msg] + state["messages"])
    print(f"Business Agent Response: {response}")
    if response.tool_calls is None or len(response.tool_calls) == 0:
        response = HumanMessage(content=response.content, )
    return {"messages": [response]}


name_to_tool = {
    "business_retreiver": "Retriever",
    "business_schema_generator": "Schema Generator",
    "business_respond": "Respond",
}

def business_tool_choice(state: BusinessState) -> Literal["Sanitizer", "Retriever", "Respond", "Business Agent"]:
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
    response = state["messages"][-1].tool_calls[0]["args"]["response"]
    state_update = {
                "messages": [state["messages"][0],
                    HumanMessage(
                    content=f"**Business Agent** response: {response}",
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