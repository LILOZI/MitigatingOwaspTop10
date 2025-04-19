from langgraph.graph import MessagesState


class CommanderState(MessagesState):
    """State for the Commander agent."""

    token: str = None
    token_expiry: str = None
    user: str = None