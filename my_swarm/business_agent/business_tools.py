from langchain_ollama import OllamaEmbeddings, ChatOllama

from langchain_chroma import Chroma

from langchain_core.tools import tool

from langgraph.types import Command, Send

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from typing import List

embeddings = OllamaEmbeddings(model="nomic-embed-text")

intro_retriever = Chroma(
    collection_name="lebron_intro",
    embedding_function=embeddings,
    persist_directory="./lebron_intro_db"
).as_retriever(
    search_type="mmr", search_kwargs={"k": 3}
)

body_retriever = Chroma(
    collection_name="lebron_bio",
    embedding_function=embeddings,
    persist_directory="./lebron_bio_db"
).as_retriever(
    search_type="mmr", search_kwargs={"k": 3}
)

@tool
def lebron_intro_retreiver(query: str) -> List[str]:
    """Retrieves relevant information about Lebron James.
    Use this tool when you need short answers and specific information about Lebron James.

    Args:
        query (str): The query to search for in the vector store.
    """
    intro_retriever_result = intro_retriever.invoke(query)
    if intro_retriever_result is not None:
        return [result.page_content for result in intro_retriever_result]
    else:
        return ["No relevant information found."]

@tool
def lebron_body_retreiver(query: str) -> List[str]:
    """Retrieves relevant information about Lebron James.
    Use this tool when you need larger context and broader information about Lebron James.

    Args:
        query (str): The query to search for in the vector store.
    """
    body_retriever_result = body_retriever.invoke(query)
    if body_retriever_result is not None:
        return [result.page_content for result in body_retriever_result]
    else:
        return ["No relevant information found."]

@tool 
def business_respond(response: str) -> str:
    """
    After finding a result and writing it as a message, the business agent will call this function to format the response.
    The agent will call this function with the response it has written in previous messages.

    Args:
        response (str): The response to be returned.
    """
    pass

llm_business = ChatOllama(model="llama3.2:3b-instruct-q8_0",
                          num_ctx=4096,
                          temperature=0.4,
                          top_k=40).bind_tools([business_respond, lebron_intro_retreiver,
                                                lebron_body_retreiver])
