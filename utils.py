import streamlit as st
import sqlite3
import hashlib
import hmac
import secrets
import re
from pathlib import Path
from database import get_connection, init_db


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_bytes(16)

    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200000
    )

    return salt.hex() + "$" + derived.hex()


def verify_password(password, stored_password):
    try:
        salt_hex, hash_hex = stored_password.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            200000
        )

        return hmac.compare_digest(actual_hash, expected_hash)
    except (ValueError, TypeError):
        return hmac.compare_digest(password, stored_password)


def create_user(username, password):
    username = username.strip()

    if not username or not password:
        return False, "Username and password are required."

    if len(username) > 100:
        return False, "Username must be 100 characters or fewer."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hash_password(password))
            )
        return True, "Account created successfully. Please log in."
    except sqlite3.IntegrityError:
        return False, "Username already exists."


def verify_user(username, password):
    with get_connection() as conn:
        user = conn.execute(
            "SELECT id, password FROM users WHERE username = ?",
            (username.strip(),)
        ).fetchone()

        if user is None:
            return None

        user_id, stored_password = user

        if verify_password(password, stored_password):
            return user_id

        return None


def check_authentication():
    st.session_state.setdefault("user_id", None)
    st.session_state.setdefault("username", None)
    st.session_state.setdefault("register", False)

    return st.session_state.user_id is not None


def login_section():
    st.title("MindCare - Mental Health Journal")

    if st.session_state.register:
        st.subheader("Create Account")

        with st.form("register_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input(
                "Confirm Password", type="password"
            )
            submitted = st.form_submit_button("Register")

        if submitted:
            if password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, message = create_user(username, password)

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
        st.info("**Crisis Help:** Seek local emergency support if in immediate danger.")

    with col2:
        st.info("**Support:** Contact someone you trust or a mental health professional.")

    with col3:
        st.info("**Therapy:** Consider a qualified mental health professional.")


@st.cache_resource
def load_model():
    try:
        from transformers import pipeline

        return pipeline(
            "sentiment-analysis",
            model="distilbert/distilbert-base-uncased-finetuned-sst-2-english"
        )
    except Exception as error:
        st.warning(
            f"Sentiment model could not be loaded: {error}. "
            "Entries can still be saved without automated analysis."
        )
        return None


def sidebar_content():
    with st.sidebar:
        st.markdown("### Welcome to MindCare!")
        st.write("Track your journal entries and reflect on your mood.")

        if st.button("Logout"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()

        st.markdown("---")
        st.markdown("### Quick Tips")
        st.markdown(
            "- Write regularly\n"
            "- Be honest about your feelings\n"
            "- Review your patterns\n"
            "- Seek support when needed"
        )


def create_pdf(entries, username):
    from io import BytesIO
    from xml.sax.saxutils import escape
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer
    )
    from reportlab.lib.styles import getSampleStyleSheet
    from datetime import datetime

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(
            "MindCare Journal - " + escape(str(username)),
            styles["Title"]
        ),
        Spacer(1, 12),
        Paragraph(
            "Exported on: " + datetime.now().strftime("%B %d, %Y"),
            styles["Normal"]
        ),
        Spacer(1, 12)
    ]

    for date, entry_text, emotion, sentiment, confidence in entries:
        story.append(
            Paragraph(escape(str(date)), styles["Heading2"])
        )
        story.append(
            Paragraph(escape(str(entry_text)).replace("\n", "<br/>"),
                      styles["Normal"])
        )
        score = float(confidence or 0) * 100
        story.append(
            Paragraph(
                f"Sentiment: {escape(str(sentiment or 'UNKNOWN'))} "
                f"({score:.1f}% model confidence)",
                styles["Italic"]
            )
        )
        story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()