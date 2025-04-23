import streamlit as st
from uuid import uuid4

import json

from langchain_chroma import Chroma

st.markdown("""
    <style>
    .user-message {
        background-color: #d4f8c4;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        text-align: right;
        color: #000000; /* Make text dark */
    }

    .bot-message {
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        text-align: left;
        color: #000000; /* Make text dark */
    }
    </style>
""", unsafe_allow_html=True)

user_history = Chroma(
    collection_name="user_history",
    embedding_function="granite-embedding:30m",
    persist_directory="./chroma_user_history",
)

# Initializes the LangGraph swarm agents
@st.cache_resource
def init_supervisor():
   from my_swarm.swarm import supervisor
   return supervisor

supervisor = init_supervisor()

# Session state setup
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("messages", [])
st.session_state.setdefault("thread_id", str(uuid4()))

st.title("🧠 Chatbot with Agent-Based Auth")

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
        # Create temporary app with InMemorySaver for login/signup
        # Ask agent to handle auth
        result = supervisor.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": f"{action.lower()} username={username} password={password}"
                }
            ]
            })
        print(result["messages"][-1])
        result = json.loads(result["messages"][-1].content)
        if not result["security_issue"]:
            st.session_state["logged_in"] = True if action == "Log in" else False
            st.session_state["current_user"] = username
            st.session_state["messages"] = []  # reset conversation
            st.session_state["thread_id"] = str(uuid4())
            st.success(f"✅ {result["response"]}")
        else:
            st.error(f"❌ {result["response"]}")
        

else:
    # username = st.session_state["current_user"]
    # st.subheader(f"💬 Chatting as: {username}")
    # for msg in st.session_state["messages"]:
    #     st.write(f"**{msg['role'].capitalize()}:** {msg['content']}")

    # with st.form(key="chat_form", clear_on_submit=True):
    #     user_input = st.text_input("Message:")
    #     send = st.form_submit_button("Send")

    # if send and user_input:
    #     st.session_state["messages"].append({"role": "user", "content": user_input})

    #     try:
    #         # Compile the app with user's Chroma checkpointer
    #         result = supervisor.invoke(
    #             {"messages": st.session_state["messages"]},
    #         )

    #         st.session_state["messages"].append(
    #             {
    #                 "role": "assistant",
    #                 "content": result["messages"][-1].content,
    #             }
    #         )
    #         st.rerun()

    #     except Exception as e:
    #         st.error(f"⚠️ supervisor Error: {e}")
    username = st.session_state["current_user"]
    st.subheader(f"💬 Chatting as: {username}")

    for msg in st.session_state['messages']:
        if msg['role'] == 'user':
            st.markdown(f"<div class='user-message'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-message'>{msg['content']}</div>", unsafe_allow_html=True)


    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Message:")
        send = st.form_submit_button("Send")

    if send and user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})

        try:
            # Compile the app with user's Chroma checkpointer
            result = supervisor.invoke(
                {"messages": st.session_state["messages"]},
            )

            st.session_state["messages"].append(
                {
                    "role": "assistant",
                    "content": result["messages"][-1].content,
                }
            )
            st.rerun()

        except Exception as e:
            st.error(f"⚠️ supervisor Error: {e}")