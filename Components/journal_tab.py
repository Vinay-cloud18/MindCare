import streamlit as st
import re
from datetime import datetime
from database import add_user_entry


def map_emotion_to_sentiment(label):
    label = label.strip().upper()

    if label in ("POSITIVE", "LABEL_1"):
        return "POSITIVE"

    if label in ("NEGATIVE", "LABEL_0"):
        return "NEGATIVE"

    return "UNKNOWN"


def contains_concerning_phrase(text):
    patterns = [
        r"\bkill myself\b",
        r"\bwant to die\b",
        r"\bi want to end my life\b",
        r"\bend my life\b",
        r"\bthinking about suicide\b",
        r"\bsuicidal thoughts\b",
        r"\bhurt myself\b"
    ]

    text = text.lower()
    return any(re.search(pattern, text) for pattern in patterns)


def journal_tab(sentiment_pipeline):
    st.header("Today's Journal Entry")

    selected_date = st.date_input(
        "Select Date",
        value=datetime.now().date()
    )

    journal_entry = st.text_area(
        "How are you feeling today?",
        height=200,
        placeholder="Write about your thoughts, feelings, and experiences..."
    )

    mood_rating = st.slider(
        "Rate your overall mood today",
        min_value=1,
        max_value=10,
        value=5
    )

    st.write(f"Mood rating: {mood_rating}/10")

    if st.button("Save Entry", type="primary"):
        text = journal_entry.strip()

        if text == "":
            st.warning("Please write something before saving.")
            return

        if sentiment_pipeline is None:
            emotion = "UNAVAILABLE"
            sentiment = "UNKNOWN"
            confidence = None
        else:
            try:
                result = sentiment_pipeline(text[:512])[0]
                emotion = result["label"].upper()
                sentiment = map_emotion_to_sentiment(result["label"])
                confidence = float(result["score"])
            except Exception as error:
                st.error(f"Sentiment analysis failed: {error}")
                return

        add_user_entry(
            st.session_state.user_id,
            selected_date.strftime("%Y-%m-%d"),
            text,
            emotion,
            sentiment,
            confidence
        )

        st.success("Entry saved successfully!")

        if sentiment == "POSITIVE":
            st.markdown("### 😊 Thank you for checking in with yourself!")
        elif sentiment == "NEGATIVE":
            st.markdown(
                "### 💙 Difficult days happen. "
                "Consider taking a break or talking with someone you trust."
            )
        elif sentiment == "NEUTRAL":
            st.markdown("### 🍃 Thank you for taking time to reflect.")
        else:
            st.info(
                "Your entry was saved, but automated sentiment "
                "analysis was unavailable."
            )

        st.markdown(f"**Model label:** {emotion}")
        st.markdown(f"**Overall sentiment:** {sentiment}")

        if confidence is not None:
            st.caption(
                f"Model confidence: {confidence * 100:.1f}%"
            )

        if contains_concerning_phrase(text):
            st.warning(
                "Your entry contains wording that may indicate distress. "
                "Automated text analysis cannot assess your safety. "
                "If this reflects how you feel now, consider reaching out "
                "to someone you trust or a mental health professional. "
                "If you are in immediate danger, contact local emergency "
                "services."
            )