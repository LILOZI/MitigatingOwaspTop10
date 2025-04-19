from my_swarm.security_agent.security_state import SecurityState

from langchain_ollama import OllamaEmbeddings

from langchain_chroma import Chroma

from langchain.schema import Document

from langchain_core.tools import tool

from langchain_core.messages import SystemMessage

from langgraph.types import Command, Send

import logging

import jwt

import bcrypt

import os

import re

import datetime

from dotenv import load_dotenv, dotenv_values 

load_dotenv() 

# accessing and printing value
SECRET_KEY = os.getenv("SECRET_HASHING_KEY")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

EMBEDDING_MODEL = OllamaEmbeddings(model="granite-embedding:30m")

USER_COLLECTION = "users"
PERSIST_USERS_DIR = "./chroma_users"

REPORT_COLLECTION = "security_reports"
PERSIST_REPORTS_DIR = "./chroma_security_reports"
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

@tool
def add_user(state: SecurityState) -> SecurityState:
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

@tool
def authenticate_fn(state: SecurityState) -> SecurityState:
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
                        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)
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

def verify_token(state: SecurityState) -> SecurityState:
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