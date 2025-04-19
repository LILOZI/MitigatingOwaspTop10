import streamlit as st
# Placeholder for your LangGraph agent import
from my_swarm.swarm import swarm, StreamlitCallbackHandler

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Page title
st.title("Secured Chatbot")

# Render existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User input
user_input = st.chat_input("Type your message here...")
if user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("assistant"):
        # Stream response with callback
        st_callback = StreamlitCallbackHandler(st.container())
        response_stream = swarm.stream(
            {"input": user_input}, callbacks=[st_callback]
        )
        # The callback handler will display chunks automatically
        for _ in response_stream:
            pass
        # Optionally, capture full response
        full_response = st_callback.get_full_text()
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
