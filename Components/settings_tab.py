import streamlit as st
import random
from datetime import datetime
from database import get_connection


def settings_tab():
    st.header("Settings & Resources")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Account Settings")
        st.info(f"Logged in as: **{st.session_state.username}**")

        if st.button("Logout"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()

        st.subheader("Notification Settings")

        with get_connection() as conn:
            settings = conn.execute(
                """
                SELECT daily_reminder, reminder_time
                FROM user_settings
                WHERE user_id = ?
                """,
                (st.session_state.user_id,)
            ).fetchone()

        reminder_default = bool(settings[0]) if settings else True

        reminder = st.checkbox(
            "Enable daily reminders",
            value=reminder_default
        )

        default_time = datetime.now().replace(
            hour=9, minute=0, second=0, microsecond=0
        ).time()

        if settings and settings[1]:
            try:
                default_time = datetime.strptime(
                    settings[1], "%H:%M"
                ).time()
            except ValueError:
                pass

        reminder_time = st.time_input(
            "Reminder time",
            value=default_time,
            disabled=not reminder
        )

        if st.button("Save Settings"):
            with get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO user_settings (
                        user_id, daily_reminder, reminder_time
                    )
                    VALUES (?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        daily_reminder = excluded.daily_reminder,
                        reminder_time = excluded.reminder_time
                    """,
                    (
                        st.session_state.user_id,
                        int(reminder),
                        reminder_time.strftime("%H:%M")
                    )
                )

            st.success("Settings saved successfully!")

    with col2:
        st.subheader("Mental Health Resources")

        resources = [
            (
                "KIRAN Helpline",
                "1800-599-0019",
                "Government of India mental-health support."
            ),
            (
                "AASRA",
                "+91-9820466726",
                "Emotional support and suicide-prevention services."
            ),
            (
                "Emergency Services",
                "112",
                "India's emergency response number."
            )
        ]

        for name, number, description in resources:
            with st.expander(f"{name}: {number}"):
                st.write(description)

        st.subheader("Self-Care Ideas")

        self_care = [
            "Take a walk in nature 🌳",
            "Practice deep breathing for five minutes 🧘",
            "Listen to your favorite music 🎵",
            "Write down three things you're grateful for 📝",
            "Call a friend or loved one 📞",
            "Try a guided meditation 🪷"
        ]

        st.info("Today's self-care suggestion:")
        st.success(random.choice(self_care))