import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from database import get_user_entries


def analytics_tab():
    st.header("Mood Analytics")

    entries = get_user_entries(st.session_state.user_id)

    if len(entries) == 0:
        st.info("No journal entries yet. Start by writing your first entry!")
        return

    df = pd.DataFrame(
        entries,
        columns=[
            "date", "entry_text", "emotion", "sentiment", "confidence"
        ]
    )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["sentiment"] = df["sentiment"].fillna("UNKNOWN").str.upper()
    df["emotion"] = df["emotion"].fillna("UNKNOWN")
    df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce")

    df = df.dropna(subset=["date"]).sort_values("date")

    if df.empty:
        st.warning("No valid journal dates are available.")
        return

    sentiment_map = {
        "NEGATIVE": 0,
        "NEUTRAL": 1,
        "POSITIVE": 2
    }

    df["sentiment_value"] = df["sentiment"].map(sentiment_map)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Mood Trend Over Time")

        trend_df = df.dropna(subset=["sentiment_value"])

        if trend_df.empty:
            st.info("No recognized sentiment results are available.")
        else:
            fig = px.line(
                trend_df,
                x="date",
                y="sentiment_value",
                markers=True,
                title="Your Emotional Journey",
                labels={
                    "sentiment_value": "Sentiment",
                    "date": "Date"
                },
                hover_data=["sentiment"]
            )

            fig.update_layout(
                yaxis=dict(
                    tickmode="array",
                    tickvals=[0, 1, 2],
                    ticktext=["Negative", "Neutral", "Positive"],
                    range=[-0.2, 2.2]
                )
            )

            st.plotly_chart(
                fig,
                width="stretch",
                key="mood_trend_chart"
            )

    with col2:
        st.subheader("Emotion Distribution")

        counts = df["emotion"].value_counts().reset_index()
        counts.columns = ["emotion", "count"]

        fig2 = px.pie(
            counts,
            values="count",
            names="emotion",
            title="Recorded Model Labels",
            hole=0.35
        )

        st.plotly_chart(
            fig2,
            width="stretch",
            key="emotion_distribution_chart"
        )

    st.subheader("Your Journaling Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Entries", len(df))

    with col2:
        positive_count = int((df["sentiment"] == "POSITIVE").sum())
        st.metric("Positive Entries", positive_count)

    with col3:
        entry_dates = set(df["date"].dt.date)
        check_date = datetime.now().date()
        streak = 0

        while check_date in entry_dates:
            streak += 1
            check_date -= timedelta(days=1)

        st.metric("Current Streak", f"{streak} days")

    with col4:
        valid_confidence = df["confidence"].dropna()

        if valid_confidence.empty:
            st.metric("Avg. Confidence", "N/A")
        else:
            st.metric(
                "Avg. Confidence",
                f"{valid_confidence.mean() * 100:.1f}%"
            )

    st.caption(
        "Sentiment predictions are automated estimates, not "
        "clinical assessments."
    )
