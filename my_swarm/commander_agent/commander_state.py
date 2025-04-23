from langgraph.prebuilt.chat_agent_executor import AgentState
    
from pydantic import Field

from typing import Annotated, Literal

def set_str(str1, str2):
    return str2
def set_bool(bool1, bool2):
    return bool2

class CommanderState(AgentState):
    """State for the Commander agent."""
    username: Annotated[str, set_str] = Field(default=None, description="Username of the logged-in user")
    is_authenticated: Annotated[bool, set_bool] = Field(default=False, description="Authentication status of the user")
    auth_token: Annotated[str, set_str] = Field(default=None, description="Authentication token of the user")