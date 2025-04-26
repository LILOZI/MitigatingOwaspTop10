import bcrypt
import jwt
import datetime
import logging
import re
from typing import TypedDict, Literal

from langchain_core.messages.tool import ToolCall

from langchain_chroma import Chroma
from langchain.schema import Document
from langchain.tools import tool
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage

from langgraph.types import Command, Send

from my_swarm.security_agent.security_state import SecurityState
import os
import re

import json

from dotenv import load_dotenv 

load_dotenv() 

# accessing and printing value
SECRET_HASHING_KEY = os.getenv("SECRET_HASHING_KEY")

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


# === Utility Functions ===
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

def log_security_event(username: str, message: str):
    logger.warning(message)
    report_store.add_documents([
        Document(page_content=message, metadata={"username": username})
    ])

def get_security_report(username: str) -> str:
    results = report_store.similarity_search(username, k=10)
    filtered = [doc.page_content for doc in results if doc.metadata.get("username") == username]
    return ", ".join(filtered)

# === TOOLS ===
@tool
def add_user(username: str, password: str, role: str) -> str:
    """
    Register a new user. Only the 'user' role is allowed; any attempt to specify a different role is logged.
    
    Args:
        username (str): The username of the user to register.
        password (str): The password of the user to register.
        role (str): The role of the user. Only 'user' is allowed.
    """
    logger.info(f"Attempting to add user: {username}")
    try:
        if role.lower() != "user":
            log_security_event(username, f"Attempt to register as '{role}' was ignored. User assigned role 'user'.")
        enforced_role = "user"

        results = user_store.similarity_search(query=username, k=5)
        for doc in results:
            if doc.metadata.get("username") == username:
                logger.warning(f"Username '{username}' is already taken.")
                return "Error:❌ Sign up Failed.\n" \
                f"A user with the username '{username}' already exists. Please choose a different username."

        if not is_valid_password(password):
            return "❌ Password does not meet complexity requirements.\n" \
                   "Password must be at least 8 characters long and include uppercase, lowercase, number, and symbol."

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        doc = Document(
            page_content=hashed_password,
            metadata={"username": username, "role": enforced_role}
        )
        user_store.add_documents([doc])
        logger.info(f"User '{username}' added successfully with role '{enforced_role}'.")
        return f"✅ User '{username}' added."
    except Exception as e:
        logger.error(f"Failed to add user '{username}': {e}")
        return f"❌ Failed to add user: {e}"

@tool
def authenticate_user(username: str, password: str) -> str:
    """Authenticate a user using a password and return a JWT token and security report if successful.
    
    Args:
        username (str): The username of the user to authenticate.
        password (str): The password of the user to authenticate.
    """
    logger.info(f"Authenticating user: {username}")
    try:
        results = user_store.similarity_search(query=username, k=5)
        for doc in results:
            if doc.metadata.get("username") == username:
                stored_hash = doc.page_content.encode()
                if bcrypt.checkpw(password.encode(), stored_hash):
                    payload = {
                        "user": username,
                        "role": doc.metadata.get("role"),
                        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)
                    }
                    token = jwt.encode(payload, SECRET_HASHING_KEY, algorithm="HS256")
                    report = get_security_report(username)
                    result = "✅ Authentication successful. Token generated."
                    if report:
                        result += f" Security Report: {report}"
                    return result + f" Token: {token}"
        logger.warning(f"Authentication failed for user: {username} - Invalid credentials.")
        return "❌ Authentication failed - Invalid credentials."
    except Exception as e:
        logger.error(f"Authentication error for user '{username}': {e}")
        return f"❌ Error during authentication: {e}"

@tool
def verify_token(username: str, token: str) -> str:
    """
    Verify a JWT token and return the decoded user and role if valid.

    Args:
        username (str): The username to verify against the token.
        role (str): The role to verify against the token.
        token (str): The JWT token to verify.
    """
    logger.info("Verifying token...")
    try:
        decoded = jwt.decode(token, SECRET_HASHING_KEY, algorithms=["HS256"])
        if decoded["user"] != username:
            logger.warning(f"Token verification failed: Token does not match user '{username}'.")
            return "❌ Token does not match user."
        # if decoded["role"] != role:
        #     logger.warning(f"Token verification failed: Token does not match role 'user'.")
        #     return "❌ Token does not match role 'user'."
        logger.info(f"Token valid for user: {decoded['user']} with role: {decoded['role']}")
        return f"✅ Token valid for user '{decoded['user']}' with role '{decoded['role']}'."
    except jwt.ExpiredSignatureError:
        logger.warning("Token verification failed: Token expired.")
        return "❌ Token expired."
    except jwt.InvalidTokenError:
        logger.warning("Token verification failed: Invalid token.")
        return "❌ Invalid token."
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        return f"❌ Error verifying token: {e}"


access_control_tools = {
    "add_user": add_user,
    "authenticate_user": authenticate_user,
    "verify_token": verify_token
}


def execute_access_control(state: SecurityState) -> Command:
    """Execute access control based on the user's role and token."""
    print("Executing access control...")
    print("State:", state)
    if state["username"] == "":
        print("No username found in state.")
        return Command(
            goto=Send("Security Agent", arg={"messages": state["messages"]}),
        )
    print("hey")
    if isinstance(state["messages"][-1], AIMessage):
        tool_call = state["messages"][-1].tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        toll_id = tool_call["id"]

        try:
            response = access_control_tools[tool_name].invoke(tool_call)
            # response_dict = {
            #     "content": response.content,
            #     "name": tool_name,
            #     "tool_call_id": toll_id
            # }
            
            state_update = {
                "messages": [state["messages"][0],
                    HumanMessage(
                    content=f"**Security Agent** response: {response.content}",
                    # tool_calls=[ToolCall(
                    #     name=tool_name,
                    #     args={"transfer_to": "Supervisor"},
                    #     id="1",
                    # )],
                ),
                ToolMessage(
                    content=f"**Security Agent** Handoff → **Supervisor**",
                    name="handoff_to_supervisor",
                    tool_call_id="1",
                )],
            }
            if tool_name == "verify_token":
                state_update["auth_token"] = tool_args["token"]
                state_update["username"] = tool_args["username"]
                state_update["is_authenticated"] = True
                
            if tool_name == "authenticate_user":
                token = re.search(r'Token: ([^ ]+) ', response.content)
                state_update["username"] = tool_args["username"]
                state_update["auth_token"] = token.group(1) if token else ""
                state_update["is_authenticated"] = True if token else False
                
            print("State update:", state_update)
            return Command(
                goto=Send("Supervisor", arg=state_update),
                update=state_update,
                graph=Command.PARENT
            )
        except KeyError:
            response = f"❌ Tool '{tool_name}' not found."
            return Command(
                goto="Supervisor",
                update={"messages": [SystemMessage(
                    content=f"{response}",
                )]},
                graph=Command.PARENT
            )
        except Exception as e:
            response = f"❌ Error executing tool '{tool_name}': {e}"
            return Command(
                goto="Supervisor",
                update={"messages": [SystemMessage(
                    content=f"{response}",
                )]},
                graph=Command.PARENT
            )



 
