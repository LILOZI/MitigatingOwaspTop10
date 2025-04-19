import jwt
import bcrypt
import datetime
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document

# === Setup Embeddings and Chroma ===
embedding_model = OllamaEmbeddings(model="granite-embedding:30m")  # or another model you prefer

user_store = Chroma(
    collection_name="users",
    embedding_function=embedding_model,
    persist_directory="./chroma_users"  # optional: enables persistence
)

# TBA
# === Secret for JWT ===
SECRET_KEY = "your_super_secret_key"

# === Add a new user ===
def add_user(username, password):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    doc = Document(
        page_content=hashed_pw,
        metadata={"username": username}
    )

    user_store.add_documents([doc])
    print(f"✅ User '{username}' added.")

# === Authenticate user ===
def authenticate_user(username, password):
    results = user_store.similarity_search(query=username, k=2)
    for doc in results:
        if doc.metadata.get("username") == username:
            stored_hash = doc.page_content.encode()
            return bcrypt.checkpw(password.encode(), stored_hash)
    return False

# === Generate JWT ===
def generate_token(username, password):
    if not authenticate_user(username, password):
        return None

    payload = {
        "user": username,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# === Verify JWT ===
def verify_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return "Token expired"
    except jwt.InvalidTokenError:
        return "Invalid token"

# === Example Usage ===
# add_user("alice", "securepassword")  # run once to add

username = "alice"
password = "securepassword"

token = generate_token(username, password)
if token:
    print("✅ Token:", token)
    print("🔍 Decoded:", verify_token(token))
else:
    print("❌ Authentication failed")
