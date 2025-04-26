from langchain_ollama import OllamaEmbeddings, ChatOllama

from langchain_chroma import Chroma

from langchain_core.tools import tool

from langgraph.types import Command, Send

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

embeddings = OllamaEmbeddings(model="granite-embedding:30m")

business_vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory="./business_policies_db",  # Where to save data locally, remove if not necessary
)


business_retriever = business_vector_store.as_retriever(
    search_type="mmr", search_kwargs={"k": 4, "fetch_k": 5}
)

@tool
def business_retreiver(query: str) -> str:
    """
    Retrieves relevant information from the business vector store based on the query.

    Args:
        query (str): The query to search for in the vector store.
    """
    pass

@tool
def business_schema_generator():
    """
    Generates a json schema for the bussiness answer to be in.
    """
    
    pass

@tool 
def business_respond(response: str) -> str:
    """
    After finding a result and writing it as a message, the business agent will call this function to format the response.
    The agent will call this function with the response it has written in previous messages.

    Args:
        response (str): The response to be returned.
    """
    pass

llm_business = ChatOllama(model="llama3.2:3b",
                          num_ctx=4096,
                          temperature=0.2,
                          top_k=20).bind_tools([business_respond])