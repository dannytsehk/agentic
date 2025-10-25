import streamlit as st
import requests
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Streamlit page configuration
st.set_page_config(page_title="Wai Tse ChatBot", layout="centered")
st.title("🤖 Wai Tse ChatBot")

# Environment variables
POE_API_KEY = os.getenv("POE_API_KEY")
SENDER_EMAIL = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Validate environment variables
if not all([POE_API_KEY, SENDER_EMAIL, EMAIL_PASSWORD]):
    st.error("Missing environment variables. Please check your .env file.")
    st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Function to send email (no attachment)
def send_email(receiver_email, subject, body):
    try:
        msg = EmailMessage()
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, EMAIL_PASSWORD)
            smtp.send_message(msg)
        st.success("Email sent successfully!")
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

# Chat input
user_input = st.chat_input("Say something...")
if user_input:
    if "hello" in user_input.lower():
        custom_response = "Hi there! You said 'Hello', so I'm giving you a special greeting! 😊"
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "assistant", "content": custom_response})
        st.chat_message("assistant").markdown(custom_response)
        st.success("Detected 'Hello' and triggered custom action!")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").markdown(user_input)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {POE_API_KEY}"
        }
        payload = {
            "model": "ChatBot_CSS",
            "messages": [{"role": "user", "content": user_input}]
        }

        try:
            response = requests.post("https://api.poe.com/v1/chat/completions", headers=headers, json=payload)
            if response.status_code == 200:
                bot_reply = response.json()["choices"][0]["message"]["content"]
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                st.chat_message("assistant").markdown(bot_reply)

                if "Are you confirmed to send an email" in bot_reply:
                    st.success("Detected email confirmation request from LLM!")
                    if st.button("Confirm Email Sending"):
                        receiver_email = "wai.tse.hk@outlook.com"
                        subject = "Test Email from Wai Tse ChatBot"
                        body = "This is a test email sent from the Wai Tse ChatBot."
                        send_email(receiver_email, subject, body)
            else:
                st.error(f"Poe API error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to Poe API: {str(e)}")

# Debug section
if st.checkbox("Show Debug Info"):
    st.write("Environment Variables:")
    st.write(f"POE_API_KEY: {'Set' if POE_API_KEY else 'Not set'}")
    st.write(f"EMAIL_ADDRESS: {'Set' if SENDER_EMAIL else 'Not set'}")
    st.write(f"EMAIL_PASSWORD: {'Set' if EMAIL_PASSWORD else 'Not set'}")
