from langchain_ollama import ChatOllama
from typing import Annotated, Dict, Callable, Set, List

from langchain_core.tools import tool, BaseTool, InjectedToolCallId
from langchain_core.messages import ToolMessage, BaseMessage, HumanMessage, AIMessage
from pydantic import BaseModel
from langgraph.types import Command
from langgraph.prebuilt import InjectedState

###############################################################################
# ADVANCED HAND‑OFF TOOL
###############################################################################

def create_custom_handoff_tool(
    *,
    agent_name: str,
    name: str | None = None,
    description: str | None = None,
    # ───────────────────────── STATE FILTER OPTIONS ──────────────────────────
    include_keys: Set[str] | None = None,
    exclude_keys: Set[str] | None = None,
    n_history: int | None = 6,
    message_filter: Callable[[BaseMessage], bool] | None = None,
    custom_filter: Callable[[Dict], Dict] | None = None,
    # ───────────────────────── TARGET‑NODE SUPPORT ───────────────────────────
    target_key: str = "",          # where we store the entry hint
    graph_name: str = ""
) -> Callable:
    """
    Returns a LangChain tool that delegates control to ``agent_name``.

    Parameters
    ----------
    agent_name: str
        The *sub‑graph* (or sibling agent) to wake up next.

    State filtering
    ---------------
    - ``include_keys``   : only these top‑level keys survive.  
    - ``exclude_keys``   : keys to drop (overrides include).  
    - ``n_history``      : trim the ``messages`` list to the last *n* items.  
    - ``message_filter`` : predicate that decides which messages stay.  
    - ``custom_filter``  : callable(state) → new_state for *full* control.

    Target node
    -----------
    The caller may specify ``target_node``.  We embed it in the hand‑off state
    under ``target_key`` and leave it to the delegate graph to act on.
    """

    if name is None:
        name = f"delegate_to_{agent_name}"
    if description is None:
        description = f"Hand off control to the '{agent_name}' sub‑graph."

    # ────────────────────────────── TOOL BODY ────────────────────────────────
    @tool(name, description=description)
    def _handoff(  # noqa: C901  (cyclomatic complexity is fine here)
        task_description: Annotated[
            str,
            "Optional short instruction for the next agent"
        ] = "",
        # target_node: Annotated[
        #     str,
        #     "If provided, jump the delegate graph straight to this node."
        # ] = target_key,
        state: Annotated[Dict, InjectedState] = None,
        tool_call_id: Annotated[str, InjectedToolCallId] = "",
    ):
        # 1) Build an ACK so the supervisor’s message log stays coherent
        ack = ToolMessage(
            content=f"Handoff → **{agent_name}**"
                    + (f" (node = {target_key})" if target_key else ""),
            name=name,
            tool_call_id=tool_call_id,
        )

        # 2) Start from the original state, then apply filters
        original = dict(state)

        # ---- (i) quick exit for custom filter --------------------------------
        if custom_filter is not None:
            filtered: Dict = custom_filter(original)
        else:
            filtered = {}
            for k, v in original.items():
                if (include_keys and k not in include_keys) or (exclude_keys and k in exclude_keys):
                    continue
                filtered[k] = v

            # trim / filter messages if present
            if "messages" in filtered:
                msgs: List[BaseMessage] = filtered["messages"]
                if message_filter:
                    msgs = [m for m in msgs if message_filter(m)]
                if n_history:
                    msgs = msgs[-n_history:]
                filtered["messages"] = msgs

        # 3) Enrich with book‑keeping
        filtered.setdefault("messages", []).append(ack)
        if task_description:
            filtered["task_description"] = task_description
        if target_key:
            filtered[target_key] = target_key

        # 4) Return the LangGraph Command
        graph = graph_name if graph_name != "" else Command.PARENT
        print(f"handoff tool {filtered}")
        return Command(
            goto=agent_name,        # stay compatible with vanilla supervisor
            update=filtered,
            graph=graph    # merge into parent‑graph state
        )

    return _handoff

def human_message_filter(Dict) -> Dict:
    new_dict = {}
    for k, v in Dict.items():
        if k == "messages":
            new_dict[k] = []
            for message in v:
                if type(message) == HumanMessage:
                    new_dict[k].append(message)
        else:
            new_dict[k] = v
    return new_dict

def credential_filters(state: Dict) -> Dict:
    """Filter to keep only credential-related keys."""
    # Keep only the keys related to credentials
    filtered_state = {}
    filtered_state["messages"] = []
    for message in state["messages"]:
        if type(message) == HumanMessage:
            filtered_state["messages"].append(message)
    if state["username"] != "":
        filtered_state["username"] = state["username"]
        filtered_state["is_authenticated"] = state["is_authenticated"]
        filtered_state["auth_token"] = state["auth_token"]
    return filtered_state

authentication_tool = create_custom_handoff_tool(
        agent_name="Security Agent",
        name="delegate_to_security_agent_for_authentication",
        description="Delegate sign ins, log ins and authentication related tasks to the Security Agent.",
        custom_filter=credential_filters,
        target_key="Access control",
        n_history=1,
        graph_name="Security Agent",
    )

validate_response_tool = create_custom_handoff_tool(
        agent_name="Security Agent",
        name="delegate_to_security_agent_for_output_validation",
        description="Validate the output of the business agent to make sure it does not contain any information we do not want to share with the user.",
        n_history=2,
        custom_filter=human_message_filter,
        target_key="Validate Output",
        graph_name="Security Agent",
    )

validate_input_tool = create_custom_handoff_tool(
        agent_name="Security Agent",
        name="delegate_to_security_agent_for_input_validation",
        description="Validate the user's input to make sure it does not contain any malicious content that attempt to bypass the system instructions.",
        n_history=1,
        custom_filter=human_message_filter,
        target_key="Validate Input",
        graph_name="Security Agent",
    )

ask_business_tool = create_custom_handoff_tool(
        agent_name="Business Agent",
        name="delegate_to_business_agent",
        description="Delegate task to the Business Agent to answer business-related questions.",
        n_history=1,
        custom_filter=human_message_filter,
        graph_name="Business Agent",
        target_key="Business Agent",
    )

tools = [
    authentication_tool,
    validate_response_tool,
    validate_input_tool,
    ask_business_tool,
]

llm_commander = ChatOllama(model="llama3.2:3b-instruct-q8_0",
                           temperature=0.0,
                           top_k=30).bind_tools(tools)


if __name__ == "__main__":
    print("Commander Agent tools loaded.")
    print(tools[0])
    print("-----------------")
    print(tools[1])
    print("-----------------")
    print(tools[2])
    print("-----------------")