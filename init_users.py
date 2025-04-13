import bcrypt
import json
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document

# === Setup Embeddings and Chroma ===
embedding_model = OllamaEmbeddings(model="granite-embedding:30m")  # or another model you prefer

user_store = Chroma(
    collection_name="users",
    embedding_function=embedding_model,
    persist_directory="./chroma_users"
)

# === Function to add user ===
def add_user(username, password, role):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    doc = Document(
        page_content=hashed_pw,
        metadata={
            "username": username,
            "role": role
        }
    )

    user_store.add_documents([doc])
    print(f"✅ User '{username}' ({role}) added to the database.")

# === Load users from JSON ===
def load_users_from_json(filepath):
    with open(filepath, "r") as f:
        users = json.load(f)
    for user in users:
        add_user(user["username"], user["password"], user["role"])
    print("✅ All users added.")

# === Run ===
if __name__ == "__main__":
    load_users_from_json("users.json")
