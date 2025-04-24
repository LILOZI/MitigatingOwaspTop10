# import bcrypt
# import jwt
# import json
# import datetime
# import logging
# import re
# from typing import TypedDict, Literal

# from langchain_community.embeddings import OllamaEmbeddings
# from langchain_chroma import Chroma
# from langchain.schema import Document
# from langgraph.graph import StateGraph, END

# # === Logging Configuration ===
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)

# # === Constants ===
# SECRET_KEY = "your_super_secret_key"
# EMBEDDING_MODEL = OllamaEmbeddings(model="nomic-embed-text")
# PERSIST_DIR = "./chroma_users"
# COLLECTION_NAME = "users"

# # === Initialize Chroma ===
# user_store = Chroma(
#     collection_name=COLLECTION_NAME,
#     embedding_function=EMBEDDING_MODEL,
#     persist_directory=PERSIST_DIR
# )

# # === State Types ===
# class AgentState(TypedDict):
#     action: Literal["add_user", "authenticate", "verify_token"]
#     username: str
#     password: str
#     role: str  # Only used in add_user
#     token: str
#     result: str

# # === Password Validation ===
# def is_valid_password(password: str) -> bool:
#     if len(password) < 8:
#         return False
#     if not re.search(r"[A-Z]", password):
#         return False
#     if not re.search(r"[a-z]", password):
#         return False
#     if not re.search(r"[0-9]", password):
#         return False
#     if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
#         return False
#     return True

# # === Helper Functions ===
# def add_user_fn(state: AgentState) -> AgentState:
#     logger.info(f"Attempting to add user: {state['username']}")
#     try:
#         # Enforce role to be 'user' regardless of input
#         if state.get("role") and state["role"].lower() != "user":
#             logger.warning(f"Requested role '{state['role']}' ignored. User '{state['username']}' will be assigned role 'user'.")
#         enforced_role = "user"

#         # Check password strength
#         if not is_valid_password(state["password"]):
#             logger.warning(f"Password for user '{state['username']}' does not meet complexity requirements.")
#             state["result"] = "❌ Password must be at least 8 characters long and include uppercase, lowercase, number, and symbol."
#             return state

#         # Check if username already exists
#         results = user_store.similarity_search(query=state["username"], k=5)
#         for doc in results:
#             if doc.metadata.get("username") == state["username"]:
#                 logger.warning(f"Username '{state['username']}' is already taken.")
#                 state["result"] = "❌ Username already exists."
#                 return state

#         hashed_pw = bcrypt.hashpw(state["password"].encode(), bcrypt.gensalt()).decode()
#         doc = Document(
#             page_content=hashed_pw,
#             metadata={"username": state["username"], "role": enforced_role}
#         )
#         user_store.add_documents([doc])
#         logger.info(f"User '{state['username']}' successfully added with enforced role '{enforced_role}'.")
#         state["result"] = f"✅ User '{state['username']}' added."
#     except Exception as e:
#         logger.error(f"Failed to add user '{state['username']}': {e}")
#         state["result"] = f"❌ Failed to add user: {e}"
#     return state

# def authenticate_fn(state: AgentState) -> AgentState:
#     username = state["username"]
#     logger.info(f"Authenticating user: {username}")
#     try:
#         results = user_store.similarity_search(query=username, k=5)
#         for doc in results:
#             if doc.metadata.get("username") == username:
#                 stored_hash = doc.page_content.encode()
#                 if bcrypt.checkpw(state["password"].encode(), stored_hash):
#                     payload = {
#                         "user": username,
#                         "role": doc.metadata.get("role"),
#                         "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
#                     }
#                     state["token"] = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
#                     logger.info(f"User '{username}' authenticated successfully.")
#                     state["result"] = "✅ Authentication successful. Token generated."
#                     return state
#         logger.warning(f"Authentication failed for user: {username} - Invalid credentials.")
#         state["result"] = "❌ Authentication failed."
#     except Exception as e:
#         logger.error(f"Authentication error for user '{username}': {e}")
#         state["result"] = f"❌ Error during authentication: {e}"
#     return state

# def verify_token_fn(state: AgentState) -> AgentState:
#     token = state["token"]
#     logger.info("Verifying token...")
#     try:
#         decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#         logger.info(f"Token valid for user: {decoded['user']} with role: {decoded['role']}")
#         state["result"] = f"✅ Token valid for user '{decoded['user']}' with role '{decoded['role']}'."
#     except jwt.ExpiredSignatureError:
#         logger.warning("Token verification failed: Token expired.")
#         state["result"] = "❌ Token expired."
#     except jwt.InvalidTokenError:
#         logger.warning("Token verification failed: Invalid token.")
#         state["result"] = "❌ Invalid token."
#     except Exception as e:
#         logger.error(f"Unexpected error during token verification: {e}")
#         state["result"] = f"❌ Error verifying token: {e}"
#     return state

# # === StateGraph Setup ===
# graph = StateGraph(AgentState)

# # Define nodes
# graph.add_node("add_user", add_user_fn)
# graph.add_node("authenticate", authenticate_fn)
# graph.add_node("verify_token", verify_token_fn)

# # Routing logic
# def router(state: AgentState):
#     logger.info(f"Routing action: {state['action']}")
#     return state["action"]

# graph.set_entry_point(router)
# graph.add_edge("add_user", END)
# graph.add_edge("authenticate", END)
# graph.add_edge("verify_token", END)

# # === Compile graph ===
# auth_graph = graph.compile()

# # === Example run ===
# if __name__ == "__main__":
#     state = auth_graph.invoke({
#         "action": "add_user",
#         "username": "david",
#         "password": "pass123A!",
#         "role": "admin",  # will be ignored
#         "token": "",
#         "result": ""
#     })
#     print(state["result"])

#     state = auth_graph.invoke({
#         "action": "authenticate",
#         "username": "david",
#         "password": "pass123A!",
#         "role": "",
#         "token": "",
#         "result": ""
#     })
#     print(state["result"])
#     print("Token:", state.get("token"))

#     state = auth_graph.invoke({
#         "action": "verify_token",
#         "username": "",
#         "password": "",
#         "role": "",
#         "token": state.get("token"),
#         "result": ""
#     })
#     print(state["result"])
import bcrypt
import jwt
import json
import datetime
import logging
import re
from typing import TypedDict, Literal

from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from langgraph.graph import StateGraph, END

# === Logging Configuration ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# === Constants ===
SECRET_KEY = "your_super_secret_key"
EMBEDDING_MODEL = OllamaEmbeddings(model="nomic-embed-text")
PERSIST_USERS_DIR = "./chroma_users"
PERSIST_REPORTS_DIR = "./chroma_security_reports"
USER_COLLECTION = "users"
REPORT_COLLECTION = "security_reports"

# === Initialize Chroma Databases ===
user_store = Chroma(
    collection_name=USER_COLLECTION,
    embedding_function=EMBEDDING_MODEL,
    persist_directory=PERSIST_USERS_DIR
)

report_store = Chroma(
    collection_name=REPORT_COLLECTION,
    embedding_function=EMBEDDING_MODEL,
    persist_directory=PERSIST_REPORTS_DIR
)

# === State Types ===
class AgentState(TypedDict):
    action: Literal["add_user", "authenticate", "verify_token"]
    username: str
    password: str
    role: str  # Only used in add_user
    token: str
    result: str

# === Password Validation ===
def is_valid_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

# === Helper Functions ===
def log_security_event(username: str, message: str):
    logger.warning(message)
    report_store.add_documents([
        Document(page_content=message, metadata={"username": username})
    ])

def get_security_report(username: str) -> str:
    results = report_store.similarity_search(username, k=10)
    filtered = [doc.page_content for doc in results if doc.metadata.get("username") == username]
    return ", ".join(filtered)

def add_user_fn(state: AgentState) -> AgentState:
    logger.info(f"Attempting to add user: {state['username']}")
    try:
        if state.get("role") and state["role"].lower() != "user":
            log_security_event(state['username'], f"Attempt to register as '{state['role']}' was ignored. User assigned role 'user'.")

        enforced_role = "user"

        if not is_valid_password(state["password"]):
            logger.warning(f"Password for user '{state['username']}' does not meet complexity requirements.")
            state["result"] = "❌ Password must be at least 8 characters long and include uppercase, lowercase, number, and symbol."
            return state

        results = user_store.similarity_search(query=state["username"], k=5)
        for doc in results:
            if doc.metadata.get("username") == state["username"]:
                logger.warning(f"Username '{state['username']}' is already taken.")
                state["result"] = "❌ Username already exists."
                return state

        hashed_pw = bcrypt.hashpw(state["password"].encode(), bcrypt.gensalt()).decode()
        doc = Document(
            page_content=hashed_pw,
            metadata={"username": state["username"], "role": enforced_role}
        )
        user_store.add_documents([doc])
        logger.info(f"User '{state['username']}' successfully added with enforced role '{enforced_role}'.")
        state["result"] = f"✅ User '{state['username']}' added."
    except Exception as e:
        logger.error(f"Failed to add user '{state['username']}': {e}")
        state["result"] = f"❌ Failed to add user: {e}"
    return state

def authenticate_fn(state: AgentState) -> AgentState:
    username = state["username"]
    logger.info(f"Authenticating user: {username}")
    try:
        results = user_store.similarity_search(query=username, k=5)
        for doc in results:
            if doc.metadata.get("username") == username:
                stored_hash = doc.page_content.encode()
                if bcrypt.checkpw(state["password"].encode(), stored_hash):
                    payload = {
                        "user": username,
                        "role": doc.metadata.get("role"),
                        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                    }
                    state["token"] = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
                    logger.info(f"User '{username}' authenticated successfully.")
                    state["result"] = "✅ Authentication successful. Token generated."

                    report = get_security_report(username)
                    if report:
                        state["result"] += f" Security Report: {report}"
                    return state
        logger.warning(f"Authentication failed for user: {username} - Invalid credentials.")
        state["result"] = "❌ Authentication failed."
    except Exception as e:
        logger.error(f"Authentication error for user '{username}': {e}")
        state["result"] = f"❌ Error during authentication: {e}"
    return state

def verify_token_fn(state: AgentState) -> AgentState:
    token = state["token"]
    logger.info("Verifying token...")
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        logger.info(f"Token valid for user: {decoded['user']} with role: {decoded['role']}")
        state["result"] = f"✅ Token valid for user '{decoded['user']}' with role '{decoded['role']}'."
    except jwt.ExpiredSignatureError:
        logger.warning("Token verification failed: Token expired.")
        state["result"] = "❌ Token expired."
    except jwt.InvalidTokenError:
        logger.warning("Token verification failed: Invalid token.")
        state["result"] = "❌ Invalid token."
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        state["result"] = f"❌ Error verifying token: {e}"
    return state


def router(state: AgentState):
    logger.info(f"Routing action: {state['action']}")
    return state["action"]


# === StateGraph Setup ===
graph = StateGraph(AgentState)

graph.add_node("add_user", add_user_fn)
graph.add_node("authenticate", authenticate_fn)
graph.add_node("verify_token", verify_token_fn)
graph.add_node("router", router)



graph.set_entry_point("router")
graph.add_edge("add_user", END)
graph.add_edge("authenticate", END)
graph.add_edge("verify_token", END)

auth_graph = graph.compile()

if __name__ == "__main__":
    state = auth_graph.invoke({
        "action": "add_user",
        "username": "david",
        "password": "pass123A!",
        "role": "admin",
        "token": "",
        "result": ""
    })
    print(state["result"])

    state = auth_graph.invoke({
        "action": "authenticate",
        "username": "david",
        "password": "pass123A!",
        "role": "",
        "token": "",
        "result": ""
    })
    print(state["result"])
    print("Token:", state.get("token"))

    state = auth_graph.invoke({
        "action": "verify_token",
        "username": "",
        "password": "",
        "role": "",
        "token": state.get("token"),
        "result": ""
    })
    print(state["result"])