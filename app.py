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

# Load environment variables
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

# Function to send email
def send_email(receiver_email, subject, body, file_path=None):
    """
    Send an email with an optional file attachment using Gmail's SMTP server.
    """
    try:
        # Create the email message
        msg = EmailMessage()
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.set_content(body)

        # Add attachment if provided
        if file_path:
            if not os.path.exists(file_path):
                st.error(f"Attachment file not found: {file_path}")
                print(f"File not found: {file_path}")
                return False
            with open(file_path, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(f.name)
                msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

        # Send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, EMAIL_PASSWORD)
            smtp.send_message(msg)
        st.success("Email sent successfully!")
        print("Email sent successfully!")
        return True
    except smtplib.SMTPAuthenticationError:
        st.error("Failed to send email: Invalid email or password. Ensure you're using a Gmail App Password.")
        print("SMTP authentication error: Check email credentials")
        return False
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        print(f"Email error details: {str(e)}")
        return False

# Chat input
user_input = st.chat_input("Say something...")
if user_input:
    # Check for "Hello" first (case-insensitive)
    if "hello" in user_input.lower():
        custom_response = "Hi there! You said 'Hello', so I'm giving you a special greeting! 😊"
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "assistant", "content": custom_response})
        st.chat_message("assistant").markdown(custom_response)
        st.success("Detected 'Hello' and triggered custom action!")
    else:
        # Append user message
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

        try:
            response = requests.post("https://api.poe.com/v1/chat/completions", headers=headers, json=payload)
            if response.status_code == 200:
                bot_reply = response.json()["choices"][0]["message"]["content"]
                print("Poe API response:", bot_reply)  # Debug
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                st.chat_message("assistant").markdown(bot_reply)

                # Check for email confirmation trigger
                if "Are you confirmed to send an email" in bot_reply:
                    st.success("Detected email confirmation request from LLM!")
                    if st.button("Confirm Email Sending"):
                        st.write("Email send button clicked!")  # Debug
                        receiver_email = "wai.tse.hk@outlook.com"
                        subject = "Test Email with Attachment"
                        body = "This is a test email with an attachment."
                        # Ensure file path is correct (relative to script)
                        file_path = os.path.join(os.path.dirname(__file__), "Wai_Tse_Resume.pdf")
                        if send_email(receiver_email, subject, body, file_path):
                            st.success("Email sent successfully!")
                        else:
                            st.error("Email sending failed.")
            else:
                st.error(f"Poe API error: {response.status_code} - {response.text}")
                print(f"Poe API error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to Poe API: {str(e)}")
            print(f"Poe API error: {str(e)}")

# Debug section (optional, can be commented out in production)
if st.checkbox("Show Debug Info"):
    st.write("Environment Variables:")
    st.write(f"POE_API_KEY: {'Set' if POE_API_KEY else 'Not set'}")
    st.write(f"EMAIL_ADDRESS: {'Set' if SENDER_EMAIL else 'Not set'}")
    st.write(f"EMAIL_PASSWORD: {'Set' if EMAIL_PASSWORD else 'Not set'}")
    st.write(f"File exists (Wai_Tse_Resume.pdf): {os.path.exists(os.path.join(os.path.dirname(__file__), 'Wai_Tse_Resume.pdf'))}")
