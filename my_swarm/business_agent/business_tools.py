from langchain_ollama import OllamaEmbeddings

from langchain_chroma import Chroma

from langchain_core.tools import tool


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
