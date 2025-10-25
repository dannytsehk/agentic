import streamlit as st
import requests
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Streamlit page configuration
st.set_page_config(page_title="Wai Tse ChatBot", layout="centered")
st.title("🤖 Wai Tse ChatBot")

# Load API key and email credentials from environment
POE_API_KEY = os.getenv("POE_API_KEY")
SENDER_EMAIL = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Function to send email
def send_email(receiver_email, subject, body, file_path=None):
    try:
        # Create the email message
        msg = EmailMessage()
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.set_content(body)

        # Add attachment if provided
        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(f.name)
                msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

        # Send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

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

            # Check if LLM reply contains "Are you confirmed to send an email"
            if "Are you confirmed to send an email" in bot_reply:
                st.success("Detected 'Are you confirmed to send an email' in LLM response! Triggering custom action.")
                # Display a confirmation button for email sending
                if st.button("Confirm Email Sending"):
                    # Email details
                    receiver_email = "wai.tse.hk@outlook.com"
                    subject = "Test Email with Attachment"
                    body = "This is a test email with an attachment."
                    file_path = "Wai_Tse_Resume.pdf"  # Updated file name

                    # Send email and provide feedback
                    if send_email(receiver_email, subject, body, file_path):
                        st.write("Email sent successfully!")
                    else:
                        st.error("Email sending failed.")
        else:
            st.error("Failed to get response from Poe API.")
