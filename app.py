import streamlit as st
from auth import register_user, login_user
from chat_utils import send_message, get_messages, clear_messages  # Import clear_messages
from flask import Flask
from flask_socketio import SocketIO, emit
from threading import Thread
import time

# Initialize Flask app and SocketIO
flask_app = Flask(__name__)
socketio = SocketIO(flask_app)

# Run Flask in a separate thread
def run_flask():
    socketio.run(flask_app, use_reloader=False)

# Start the Flask app
Thread(target=run_flask).start()

# Streamlit app configuration
st.set_page_config(page_title="Chat Application", page_icon="💬", layout="centered")

# Custom CSS for styling
st.markdown("""
    <style>
        .chat-message {
            padding: 10px;
            border-radius: 15px;
            margin-bottom: 10px;
            max-width: 80%;
        }
        .user-message {
            background-color: #008080;
            color: white;
            text-align: right;
        }
        .recipient-message {
            background-color: #007BFF;
            color: white;
            text-align: left;
        }
        .message-container {
            background-color: #1E1E1E;
            padding: 20px;
            border-radius: 15px;
            max-height: 300px;
            overflow-y: auto;
        }
        input, textarea {
            font-size: 18px !important;
            border-radius: 10px !important;
            padding: 10px !important;
        }
        button {
            border-radius: 10px !important;
            padding: 10px 20px !important;
            font-size: 16px !important;
        }
        button:hover {
            background-color: #17a2b8 !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# Authentication section
if 'username' not in st.session_state:
    st.subheader("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        register_user(username, password)
        st.success("Registration successful! You can log in now.")

    st.subheader("Login")
    login_username = st.text_input("Username (Login)")
    login_password = st.text_input("Password (Login)", type="password")

    if st.button("Login"):
        if login_user(login_username, login_password):
            st.session_state['username'] = login_username
            st.success(f"Welcome, {login_username}!")
        else:
            st.error("Invalid username or password.")
else:
    if 'selected_user' not in st.session_state:
        st.subheader(f"Welcome back, {st.session_state['username']}!")
        selected_user = st.text_input("Enter the username of the person you want to message:")

        if st.button("Start Chat"):
            if selected_user:
                st.session_state['selected_user'] = selected_user
            else:
                st.error("Please enter a valid username.")
    
    else:
        # Chat screen for the selected user
        st.subheader(f"Chat with {st.session_state['selected_user']}")

        # Message display area
        chat_container = st.empty()

        def load_messages():
            with chat_container.container():
                messages = get_messages(st.session_state['username'], st.session_state['selected_user'])

                if messages:
                    messages = messages[::-1]  # Reverse the order
                    st.markdown("<div class='message-container'>", unsafe_allow_html=True)
                    
                    for msg in messages:
                        if msg["sender"] == st.session_state['username']:
                            st.markdown(
                                f'<div class="chat-message user-message"><strong>You:</strong> {msg["message"]}</div>',
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f'<div class="chat-message recipient-message"><strong>{msg["sender"]}:</strong> {msg["message"]}</div>',
                                unsafe_allow_html=True
                            )
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info(f"No previous messages with {st.session_state['selected_user']}")

        # Load messages initially
        load_messages()

        # Input for a new message and buttons (Send, Refresh, Clear Chat)
        message = st.text_input("Message")

        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            if st.button("Send"):
                if message:
                    send_message(st.session_state['username'], st.session_state['selected_user'], message)
                    socketio.emit('message', {'username': st.session_state['username'], 'message': message, 'recipient': st.session_state['selected_user']})
                    st.success("Message sent!")
                    load_messages()  # Refresh messages after sending

        with col2:
            if st.button("Refresh"):
                load_messages()  # Manually refresh messages if needed

        with col3:
            if st.button("Clear Chat"):
                clear_messages(st.session_state['username'], st.session_state['selected_user'])
                st.success("Chat cleared!")
                load_messages()  # Refresh messages after clearing

        # Simulated auto-refresh
        while True:
            load_messages()
            time.sleep(5)  # Refresh every 5 seconds
