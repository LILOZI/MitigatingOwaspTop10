from my_swarm.security_agent.security_state import SecurityState

from langgraph.types import Command, Send

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from typing import Literal

from my_swarm.security_agent.access_control import access_control_tools

from my_swarm.security_agent.security_tools import (
    llm_security,
    llm_output_validator,
    llm_input_validator,
)

from my_swarm.security_agent.prompts import (
    SYSTEM_MESSAGE_SECURITY,
    SYSTEM_MESSAGE_VALIDATE_LEBRON,
    SYSTEM_MESSAGE_INPUT_LEBRON,
)


def security_node(state: SecurityState):
    """
    This function is an agent that handles security-related tasks.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    sys_msg = SystemMessage(
        content=SYSTEM_MESSAGE_SECURITY
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
        # "Sanitizer": "Sanitizer",
        # "Retriever": "Retriever",
        # "Respond": "Respond",
        "validate_output": "Validate Output",
    }
)

# Command[Literal["Security Agent", 
                # "Access Control", "Sanitizer", "Retriever", "Respond", "Validate Output"]]:

def security_tool_choice(state: SecurityState) -> Command[Literal["Security Agent",
            "Access Control", "Validate Output"]]:
    if type(state["messages"][-1]) is AIMessage:
        print(f"Last message: {state['messages'][-1]}")
        if state["messages"][-1].tool_calls != []:
            tool_choice = state["messages"][-1].tool_calls[0]["name"]
            if tool_choice in access_control_tools.keys():
                return Command(
                    goto=name_to_node[tool_choice],
                    update={"username": state["messages"][-1].tool_calls[0]["args"]["username"]},
                )
            elif tool_choice == "validate_output":
                return Command(
                    goto="Validate Output",
                    update={},
                )
    return Command(
                    goto="Security Agent",
                    update={},
                )
    

def validate_output_helper(state: SecurityState):
    """
    This function is an agent that validates the output of the security agent.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    print("Security Agent Validating Output...")
    if type(state["messages"][-1]) is AIMessage:
        if state["messages"][-1].name == "validate_output":
            model_response = llm_output_validator.invoke(
                [SystemMessage(content=SYSTEM_MESSAGE_VALIDATE_LEBRON), state["messages"][-1]]
            )
            state_update = {
                "messages": [state["messages"][0],
                    HumanMessage(
                    content=f"**Security Agent** response: {model_response.content}",
                ),
                ToolMessage(
                    content=f"**Security Agent** Handoff → **Supervisor**",
                    name="handoff_to_supervisor",
                    tool_call_id="1",
                )],
            }
            return Command(
                goto=Send(node="Supervisor", arg=state_update),
                update={"messages": [model_response]},
                graph=Command.PARENT,
            )
    return Command(
        goto="Security Agent",
        update={},
    )

def validate_input_helper(state: SecurityState):
    """
    This function is an agent that validates the input of the security agent.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    print("Security Agent Validating Input...")
    if type(state["messages"][-2]) is HumanMessage:
        model_response = llm_input_validator.invoke(
            [SystemMessage(content=SYSTEM_MESSAGE_INPUT_LEBRON), state["messages"][-1]]
        )
        state_update = {
            "messages": [state["messages"][0],
                HumanMessage(
                content=f"**Security Agent** response: {model_response.content}",
            ),
            ToolMessage(
                content=f"**Security Agent** Handoff → **Supervisor**",
                name="handoff_to_supervisor",
                tool_call_id="1",
            )],
        }
        return Command(
            goto=Send(node="Supervisor", arg=state_update),
            update={"messages": [model_response]},
            graph=Command.PARENT,
        )
    return Command(
        goto="Security Agent",
        update={},
    )


def security_respond(state: SecurityState):
    """
    This function is an agent that handles security-related tasks.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    # print("Security Agent Responding...")
    # if type(state["messages"][-1]) is ToolMessage:
    #     if state["messages"][-1].name in access_control_tools.keys():
    #         return {"messages": [AIMessage(content=state["messages"][-1].content)]}
    # response = state["messages"][-1].content
    # return {"messages": [AIMessage(content=response)]}
    pass