
from langchain_ollama import OllamaEmbeddings, ChatOllama

from langchain_chroma import Chroma

from langchain_core.tools import tool

from langchain_core.messages import SystemMessage

from langgraph.types import Command, Send

from my_swarm.security_agent.access_control import access_control_tools

@tool
def validate_input(input: str) -> str:
    """Validate the input of the user to make sure it does not contain any malicious content 
    that attempt to bypass the system instructions.

    Args:
        input (str): The user's input to be validated.
    """
    pass

@tool
def validate_output(output: str) -> str:
    """Validate the output of the business agent to make sure it does not contain any information
    we do not want to share with the user.
    This is to prevent the business agent from leaking any information that is not allowed.
    
    Args:
        output (str): The output to be validated.
    """
    pass

llm_security = ChatOllama(model="llama3.2:3b-instruct-q8_0").bind_tools(
    list(access_control_tools.values()) + [validate_output]
)

llm_output_validator = ChatOllama(model="llama3.2:3b-instruct-q8_0"
                             , temperature=0.0,
                             top_k=20,
                             num_ctx=4096)


llm_input_validator = ChatOllama(model="llama3.2:3b-instruct-q8_0"
                             , temperature=0.0,
                             top_k=20,
                             num_ctx=4096)