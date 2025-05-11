import streamlit as st
from uuid import uuid4
import json
import regex as re

from langchain_chroma import Chroma

import base64

def image_to_base64(path):
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded}"

# === Avatar image paths (replace with your actual paths or URLs) ===
USER_AVATAR = image_to_base64("static/profileicon.jpg")
BOT_AVATAR = image_to_base64("static/Lebron.jpg")

# === Avatar-enhanced styling ===
st.markdown(f"""
    <style>
    .message-row {{
        display: flex;
        align-items: flex-start;
        margin: 10px 0;
    }}

    .avatar {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
    }}

    .user-message, .bot-message {{
        padding: 10px;
        border-radius: 10px;
        margin: 0 10px;
        max-width: 80%;
    }}

    .user-message {{
        background-color: #d4f8c4;
        color: #000;
        margin-left: auto;
        text-align: right;
    }}

    .bot-message {{
        background-color: #f0f0f0;
        color: #000;
        margin-right: auto;
        text-align: left;
    }}
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_supervisor():
    from my_swarm.swarm import supervisor
    return supervisor

supervisor = init_supervisor()

# Session state setup
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("messages", [])
st.session_state.setdefault("thread_id", str(uuid4()))
st.session_state.setdefault("current_user", None)
st.session_state.setdefault("token", None)

st.title("🧠 NBA chatbot")

# === AUTH ===
if not st.session_state["logged_in"]:
    st.subheader("🔐 Login or Sign Up via Agent")

    if st.button("Use as Guest"):
        st.session_state["logged_in"] = True
        st.session_state["current_user"] = "Guest"
        st.session_state["messages"] = []

    action = st.radio("Choose action", ["Log in", "Sign Up"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    password_confirm = st.text_input("Confirm Password", type="password") if action == "Sign Up" else None
    if action == "Sign Up" and password != password_confirm:
        st.error("Passwords do not match!")

    if st.button("Submit"):
        model_answer = supervisor.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": f"{action.lower()} username={username} password={password}"
                }
            ]
        },
        config={"configurable": {"thread_id": st.session_state["thread_id"]}},
        )
        match = re.search(r'\{(?:[^{}]|(?R))*\}', model_answer["messages"][-1].content, flags=re.DOTALL)
        result = json.loads(match.group(0)) if match else {
            "response": "Something went wrong, please try again.",
            "security_issue": True,
        }

        if not result["security_issue"]:
            st.session_state["logged_in"] = True if action == "Log in" else False
            st.session_state["current_user"] = username
            token = re.search(r'Token: ([^\s]+)', result["response"])
            st.session_state["token"] = token.group(1) if token else ""
            st.session_state["messages"] = []
            st.session_state["thread_id"] = str(uuid4())
            st.success(f"✅ {result['response']}")
        else:
            st.error(f"❌ {result['response']}")

        if st.session_state["logged_in"]:
            st.rerun()

# === CHAT ===
else:
    username = st.session_state["current_user"]
    st.subheader(f"💬 Chatting as: {username}")

    # Display chat messages with avatars
    for msg in st.session_state['messages']:
        avatar = USER_AVATAR if msg["role"] == "user" else BOT_AVATAR
        msg_class = "user-message" if msg["role"] == "user" else "bot-message"
        alignment = "row-reverse" if msg["role"] == "user" else "row"

        st.markdown(f"""
            <div class="message-row" style="flex-direction:{alignment};">
                <img src="{avatar}" class="avatar">
                <div class="{msg_class}">{msg['content']}</div>
            </div>
        """, unsafe_allow_html=True)

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Message:")
        send = st.form_submit_button("Send")

    if send and user_input:
        # Show user message immediately
        st.session_state["messages"].append({"role": "user", "content": user_input})
        st.rerun()  # Refresh immediately to render the user message first

    # Handle LLM response after rerun
    if st.session_state["messages"] and st.session_state["messages"][-1]["role"] == "user":
        try:
            model_answer = supervisor.invoke(
                {
                    "messages": st.session_state["messages"],
                    "username": st.session_state["current_user"],
                    "token": st.session_state["token"],
                },
                config={
                    "configurable": {
                        "thread_id": st.session_state["token"],
                    }
                },
            )
            match = re.search(r'\{(?:[^{}]|(?R))*\}', model_answer["messages"][-1].content, flags=re.DOTALL)
            if match:
                result = json.loads(match.group(0))
                response = result["response"]
            else:
                response = "Something went wrong, please try again."

            st.session_state["messages"].append(
                {"role": "assistant", "content": response}
            )
            st.rerun()

        except Exception as e:
            st.error(f"⚠️ supervisor Error: {e}")

