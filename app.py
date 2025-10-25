import streamlit as st
import requests
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Wai Tse ChatBot", layout="centered")
st.title("🤖 Wai Tse ChatBot")

# Load API and email credentials from environment
POE_API_KEY = os.getenv("POE_API_KEY")
sender_email = os.getenv("EMAIL_ADDRESS", "wai.tse.diary@gmail.com")
password = os.getenv("EMAIL_PASSWORD", "ajcwbbiwnkbltgys")

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

            # Check if LLM reply contains "The resume has just sent out to"
            if "The resume has just sent out to" in bot_reply:
                st.success("Detected 'The resume has just sent out to' in LLM response! Sending email.")
                
                # Extract email address from bot_reply (assuming format: "The resume has just sent out to {email}")
                try:
                    start_idx = bot_reply.find("to ") + 3
                    end_idx = bot_reply.find(".", start_idx)
                    receiver_email = bot_reply[start_idx:end_idx].strip()

                    # Email details
                    subject = "Wai Tse Resume"
                    body = "Please find my resume attached."
                    file_path = "Wai_Tse_Resume.pdf"  # Ensure this file exists in the same directory

                    # Create the email message
                    msg = EmailMessage()
                    msg["From"] = sender_email
                    msg["To"] = receiver_email
                    msg["Subject"] = subject
                    msg.set_content(body)

                    # Add attachment
                    try:
                        with open(file_path, "rb") as f:
                            file_data = f.read()
                            file_name = f.name
                        msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)
                    except FileNotFoundError:
                        st.error("Resume file not found. Please ensure 'Wai_Tse_Resume.pdf' exists.")
                        return

                    # Send the email
                    try:
                        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                            smtp.login(sender_email, password)
                            smtp.send_message(msg)
                        st.success(f"Email sent successfully to {receiver_email}!")
                    except Exception as e:
                        st.error(f"Failed to send email: {str(e)}")
                except Exception as e:
                    st.error(f"Failed to extract email address or send email: {str(e)}")
        else:
            st.error("Failed to get response from Poe API.")
