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
    st.error(f"Missing environment variables: POE_API_KEY={'Set' if POE_API_KEY else 'Not set'}, "
             f"EMAIL_ADDRESS={'Set' if SENDER_EMAIL else 'Not set'}, "
             f"EMAIL_PASSWORD={'Set' if EMAIL_PASSWORD else 'Not set'}")
    st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Function to send email (with optional attachment)
def send_email(receiver_email, subject, body, file_path=None):
    try:
        msg = EmailMessage()
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.set_content(body)

        # Add attachment if file_path provided
        if file_path and os.path.exists(file_path):
            st.info(f"Attaching file: {os.path.basename(file_path)}")
            with open(file_path, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(f.name)
                msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)
        elif file_path:
            st.warning(f"File not found: {file_path}")
            return False

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, EMAIL_PASSWORD)
            smtp.send_message(msg)
        st.success("Email sent successfully with attachment!" if file_path else "Email sent successfully!")
        return True
    except smtplib.SMTPAuthenticationError as e:
        st.error(f"Authentication error: {e}. Check App Password and 2FA.")
        return False
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

# File upload for testing
uploaded_file = st.file_uploader("Upload file for testing (optional)", type=['pdf', 'docx', 'txt'])

# Test email buttons (for debugging)
col1, col2 = st.columns(2)
with col1:
    if st.button("🧪 Test Email (No Attachment)"):
        st.write("Test email button clicked!")
        receiver_email = "wai.tse.hk@outlook.com"
        subject = "Test Email from Wai Tse ChatBot"
        body = "This is a direct test email from the Streamlit app."
        send_email(receiver_email, subject, body)

with col2:
    if st.button("📎 Test Email (With Attachment)"):
        st.write("Test email with attachment button clicked!")
        receiver_email = "wai.tse.hk@outlook.com"
        subject = "Test Email WITH Attachment"
        body = "This is a test email with an attachment from the Streamlit app."
        
        # Use uploaded file or default resume file
        test_file_path = uploaded_file.name if uploaded_file else "Wai_Tse_Resume.pdf"
        if uploaded_file:
            # Save uploaded file temporarily
            with open(test_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        send_email(receiver_email, subject, body, test_file_path)

# Show file status
if st.checkbox("Check File Status"):
    resume_exists = os.path.exists("Wai_Tse_Resume.pdf")
    st.write(f"**Wai_Tse_Resume.pdf exists:** {'✅ Yes' if resume_exists else '❌ No'}")
    if uploaded_file:
        st.write(f"**Uploaded file:** {uploaded_file.name} ({uploaded_file.size} bytes)")

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
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📧 Send Email (No Attachment)"):
                            st.write("Confirm email button clicked!")
                            receiver_email = "wai.tse.hk@outlook.com"
                            subject = "Test Email from Wai Tse ChatBot"
                            body = "This is a test email triggered by the chatbot."
                            send_email(receiver_email, subject, body)
                            st.rerun()
                    with col2:
                        if st.button("📎 Send Email (With Resume Attachment)"):
                            st.write("Confirm email with attachment button clicked!")
                            receiver_email = "wai.tse.hk@outlook.com"
                            subject = "Test Email from Wai Tse ChatBot - Resume Attached"
                            body = "This is a test email with resume attachment triggered by the chatbot."
                            send_email(receiver_email, subject, body, "Wai_Tse_Resume.pdf")
                            st.rerun()
            else:
                st.error(f"Poe API error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to Poe API: {str(e)}")

# Debug section
if st.checkbox("Show Debug Info"):
    st.write("Environment Variables:")
    st.write(f"POE_API_KEY: {'Set' if POE_API_KEY else 'Not set'}")
    st.write(f"EMAIL_ADDRESS: {SENDER_EMAIL if SENDER_EMAIL else 'Not set'}")
    st.write(f"EMAIL_PASSWORD: {'Set' if EMAIL_PASSWORD else 'Not set'}")
