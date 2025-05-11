# import streamlit as st
# from uuid import uuid4
# import json
# import regex as re

# from langchain_chroma import Chroma

# import base64

# def image_to_base64(path):
#     with open(path, "rb") as image_file:
#         encoded = base64.b64encode(image_file.read()).decode()
#         return f"data:image/png;base64,{encoded}"

# # === Avatar image paths (replace with your actual paths or URLs) ===
# USER_AVATAR = image_to_base64("static/profileicon.jpg")
# BOT_AVATAR = image_to_base64("static/Lebron.jpg")

# # === Avatar-enhanced styling ===
# st.markdown(f"""
#     <style>
#     .message-row {{
#         display: flex;
#         align-items: flex-start;
#         margin: 10px 0;
#     }}

#     .avatar {{
#         width: 40px;
#         height: 40px;
#         border-radius: 50%;
#         object-fit: cover;
#     }}

#     .user-message, .bot-message {{
#         padding: 10px;
#         border-radius: 10px;
#         margin: 0 10px;
#         max-width: 80%;
#     }}

#     .user-message {{
#         background-color: #d4f8c4;
#         color: #000;
#         margin-left: auto;
#         text-align: right;
#     }}

#     .bot-message {{
#         background-color: #f0f0f0;
#         color: #000;
#         margin-right: auto;
#         text-align: left;
#     }}
#     </style>
# """, unsafe_allow_html=True)

# @st.cache_resource
# def init_supervisor():
#     from my_swarm.swarm import supervisor
#     return supervisor

# supervisor = init_supervisor()

# # Session state setup
# st.session_state.setdefault("logged_in", False)
# st.session_state.setdefault("messages", [])
# st.session_state.setdefault("thread_id", str(uuid4()))
# st.session_state.setdefault("current_user", None)
# st.session_state.setdefault("token", None)

# st.title("🧠 NBA chatbot")

# # === AUTH ===
# if not st.session_state["logged_in"]:
#     st.subheader("🔐 Login or Sign Up via Agent")

#     if st.button("Use as Guest"):
#         st.session_state["logged_in"] = True
#         st.session_state["current_user"] = "Guest"
#         st.session_state["messages"] = []

#     action = st.radio("Choose action", ["Log in", "Sign Up"])
#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")

#     password_confirm = st.text_input("Confirm Password", type="password") if action == "Sign Up" else None
#     if action == "Sign Up" and password != password_confirm:
#         st.error("Passwords do not match!")

#     if st.button("Submit"):
#         model_answer = supervisor.invoke({
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": f"{action.lower()} username={username} password={password}"
#                 }
#             ]
#         },
#         config={"configurable": {"thread_id": st.session_state["thread_id"]}},
#         )
#         match = re.search(r'\{(?:[^{}]|(?R))*\}', model_answer["messages"][-1].content, flags=re.DOTALL)
#         result = json.loads(match.group(0)) if match else {
#             "response": "Something went wrong, please try again.",
#             "security_issue": True,
#         }

#         if not result["security_issue"]:
#             st.session_state["logged_in"] = True if action == "Log in" else False
#             st.session_state["current_user"] = username
#             token = re.search(r'Token: ([^\s]+)', result["response"])
#             st.session_state["token"] = token.group(1) if token else ""
#             st.session_state["messages"] = []
#             st.session_state["thread_id"] = str(uuid4())
#             st.success(f"✅ {result['response']}")
#         else:
#             st.error(f"❌ {result['response']}")

#         if st.session_state["logged_in"]:
#             st.rerun()

# # === CHAT ===
# else:
#     username = st.session_state["current_user"]
#     st.subheader(f"💬 Chatting as: {username}")

#     # Display chat messages with avatars
#     for msg in st.session_state['messages']:
#         avatar = USER_AVATAR if msg["role"] == "user" else BOT_AVATAR
#         msg_class = "user-message" if msg["role"] == "user" else "bot-message"
#         alignment = "row-reverse" if msg["role"] == "user" else "row"

#         st.markdown(f"""
#             <div class="message-row" style="flex-direction:{alignment};">
#                 <img src="{avatar}" class="avatar">
#                 <div class="{msg_class}">{msg['content']}</div>
#             </div>
#         """, unsafe_allow_html=True)

#     with st.form(key="chat_form", clear_on_submit=True):
#         user_input = st.text_input("Message:")
#         send = st.form_submit_button("Send")

#     if send and user_input:
#         # Show user message immediately
#         st.session_state["messages"].append({"role": "user", "content": user_input})
#         st.rerun()  # Refresh immediately to render the user message first

#     # Handle LLM response after rerun
#     if st.session_state["messages"] and st.session_state["messages"][-1]["role"] == "user":
#         try:
#             model_answer = supervisor.invoke(
#                 {
#                     "messages": st.session_state["messages"],
#                     "username": st.session_state["current_user"],
#                     "token": st.session_state["token"],
#                 },
#                 config={
#                     "configurable": {
#                         "thread_id": st.session_state["token"],
#                     }
#                 },
#             )
#             match = re.search(r'\{(?:[^{}]|(?R))*\}', model_answer["messages"][-1].content, flags=re.DOTALL)
#             if match:
#                 result = json.loads(match.group(0))
#                 response = result["response"]
#             else:
#                 response = "Something went wrong, please try again."

#             st.session_state["messages"].append(
#                 {"role": "assistant", "content": response}
#             )
#             st.rerun()

#         except Exception as e:
#             st.error(f"⚠️ supervisor Error: {e}")

import regex as re
import json

def extract_json_from_string(string: str) -> dict:
    """
    Extracts JSON from a string using regex.
    """
    try:
        # Use regex to find the JSON object in the string
        match = re.search(r'\{(?:[^{}]|(?R))*\}',string, flags=re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        else:
            return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {}

if __name__ == "__main__":
    content='{\n   "new_separation": true,\n   "new_separation_fields": {\n      "field 1": [0, 2],\n      "field 2": [2, 2],\n      "field 3": [4, 3],\n      "field 4": [7, 2], // Adjusted start offset due to field 3 length change\n      "field 5": [9, 4]  // Adjusted start offset due to previous changes\n   }\n}\n\nExplanation:\nThe mistake indicates that the Device Identifier (Destination) field spans from offset 4-6 instead of 4-5 as originally suggested. This means it\'s a 3-byte field rather than a 2-byte field. Since this change affects the length of the field, we need to adjust all subsequent fields\' start offsets accordingly:\n\n1. Field 3 (Device Identifier Destination) is now 3 bytes long\n2. Field 4 (Message Type) starts at offset 7 instead of 6\n3. Field 5 (Payload Length) starts at offset 9 instead of 8\n\nTherefore, a new separation is required to reflect these changes accurately.'
    print(content[130:140])
    result = extract_json_from_string(content)
    print(result)