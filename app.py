import streamlit as st
import requests
import os

st.set_page_config(page_title="Wai Tse ChatBot", layout="centered")
st.title("🤖 Wai Tse ChatBot")

# Load API key from environment
POE_API_KEY = os.getenv("POE_API_KEY")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Chat input
user_input = st.chat_input("Say something...")
if user_input:
    # Check for "Hello" first (case-insensitive)
    if "hello" in user_input.lower():
        # Custom action for "Hello"
        custom_response = "Hi there! You said 'Hello', so I'm giving you a special greeting! 😊"
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "assistant", "content": custom_response})
        st.chat_message("assistant").markdown(custom_response)
        st.success("Detected 'Hello' and triggered custom action!")
    else:
        # Proceed with normal flow: append user message and call Poe API
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").markdown(user_input)

        # Send to Poe API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {POE_API_KEY}"
        }
        payload = {
            "model": "ChatBot_CSS",
            "messages": [{"role": "user", "content": user_input}]
        }

        response = requests.post("https://api.poe.com/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            bot_reply = response.json()["choices"][0]["message"]["content"]
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.chat_message("assistant").markdown(bot_reply)
        else:
            st.error("Failed to get response from Poe API.")