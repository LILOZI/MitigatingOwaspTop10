
from langchain_ollama import OllamaEmbeddings

from langchain_chroma import Chroma

from langchain_core.tools import tool

from langchain_core.messages import SystemMessage

from langgraph.types import Command, Send

import jwt



embedding_model = OllamaEmbeddings(model="granite-embedding:30m")

security_vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embedding_model,
    persist_directory="./security_policies_db",  # Where to save data locally, remove if not necessary
)


security_retriever = security_vector_store.as_retriever(
    search_type="mmr", search_kwargs={"k": 4, "fetch_k": 5}
)

user_store = Chroma(
    collection_name="users",
    embedding_function=embedding_model,
    persist_directory="./chroma_users"  
)


@tool
def security_sanitizer():
    """
    This function sanitizes the state of the conversation for security-related tasks.
    It can either respond to the user, ask for more information, or exit the conversation.
    """
    print("Sanitaizing...")
    # return Command(
    #     graph="Business Agent",
    #     update={"messages": SystemMessage("Sanitize the state")},
    #     goto=Send("Business Agent", None)
    # )
    pass


@tool
def security_retriever(query: str) -> str:
    """
    Retrieves relevant information from the security vector store based on the query.

    Args:
        query (str): The query to search for in the vector store.
    """
    security_retriever.invoke(
        query=query,
)
    


# === Authenticate user ===
@tool
def authenticate_user(username, password):
    results = user_store.similarity_search(query=username, k=2)
    for doc in results:
        if doc.metadata.get("username") == username:
            stored_hash = doc.page_content.encode()
            return bcrypt.checkpw(password.encode(), stored_hash)
    return False