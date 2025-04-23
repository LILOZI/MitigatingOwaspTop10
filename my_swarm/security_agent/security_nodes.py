from my_swarm.security_agent.security_state import SecurityState

from langgraph.types import Command, Send

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from typing import Literal

from langchain_ollama import ChatOllama

from my_swarm.security_agent.access_control import access_control_tools

llm_security = ChatOllama(model="llama3.2:3b").bind_tools(
    access_control_tools.values()
)


def security_node(state:SecurityState):
    """
    This function is an agent that handles security-related tasks.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    sys_msg = SystemMessage(
        content="You are a security agent that handles security-related tasks. "
                "Given the user input, decide which security tool to use."
    )
    response = llm_security.invoke([sys_msg, state["messages"][0]])
    # try:
    #     tool_choice = SecurityChoice.validate_model_json(response)
    #     return {"messages": [AIMessage(content=tool_choice)],}
    # except Exception as e:
    #     print(f"Error validating response: {e}")
    #     return {"messages": [SystemMessage("Error validating tool choice.")]}
    print(f"Security Agent Response: {response}")
    return {"messages": [response]}


name_to_node = {
    key: "Access Control" for key in access_control_tools.keys()       
}
name_to_node.update(
    {
        "Sanitizer": "Sanitizer",
        "Retriever": "Retriever",
        "Respond": "Respond",
    }
)

def security_tool_choice(state:SecurityState) -> Command[Literal["Security Agent", 
                "Access Control", "Sanitizer", "Retriever", "Respond"]]:
    if type(state["messages"][-1]) is AIMessage:
        print(f"Last message: {state['messages'][-1]}")
        if state["messages"][-1].tool_calls is not None:
            tool_choice = state["messages"][-1].tool_calls[0]["name"]
            if tool_choice in access_control_tools.keys():
                return Command(
                    goto=name_to_node[tool_choice],
                    update={"username": state["messages"][-1].tool_calls[0]["args"]["username"]},
                )
    return Command(
                    goto="Security Agent",
                    update={"messages": [AIMessage(content=state["messages"][-1].content)]},
                )
    

def security_respond(state:SecurityState):
    """
    This function is an agent that handles security-related tasks.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    print("Security Agent Responding...")
    if type(state["messages"][-1]) is ToolMessage:
        if state["messages"][-1].name in access_control_tools.keys():
            return {"messages": [AIMessage(content=state["messages"][-1].content)]}
    response = state["messages"][-1].content
    return {"messages": [AIMessage(content=response)]}