import streamlit as st
import sqlite3
from pathlib import Path
from database import init_db

DB_PATH = Path(__file__).resolve().parent / "journal.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_user(username, password):
    username = username.strip()

    if username == "" or password == "":
        return False, "Username and password are required."

    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        return True, "Account created successfully! Please login."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()


def verify_user(username, password):
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password = ?",
            (username.strip(), password)
        )
        user = cursor.fetchone()
        return user[0] if user else None
    finally:
        conn.close()


def check_authentication():
    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    if "username" not in st.session_state:
        st.session_state.username = None

    if "register" not in st.session_state:
        st.session_state.register = False

    return st.session_state.user_id is not None


def login_section():
    init_db()

    st.title("MindCare - Mental Health Journal")

    if st.session_state.get("register", False):
        st.subheader("Create Account")

        with st.form("register_form"):
            new_username = st.text_input("Username").strip()
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input(
                "Confirm Password", type="password"
            )

            submitted = st.form_submit_button("Register")

            if submitted:
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, message = create_user(
                        new_username, new_password
                    )

                    if success:
                        st.success(message)
                        st.session_state.register = False
                        st.rerun()
                    else:
                        st.error(message)

        if st.button("Back to Login"):
            st.session_state.register = False
            st.rerun()

    else:
        st.subheader("Login to Your Journal")

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                user_id = verify_user(username, password)

                if user_id is not None:
                    st.session_state.user_id = user_id
                    st.session_state.username = username.strip()
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        if st.button("Create New Account"):
            st.session_state.register = True
            st.rerun()

    st.markdown("---")
    st.subheader("Mental Health Resources")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("**Crisis Help**: National Suicide Prevention Lifeline: 988")

    with col2:
        st.info("**Support**: Crisis Text Line: Text HOME to 741741")

    with col3:
        st.info("**Therapy**: BetterHelp, Talkspace, or local therapists")