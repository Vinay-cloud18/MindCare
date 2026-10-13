import streamlit as st
from datetime import datetime
from utils import create_pdf
from database import get_user_entries


def history_tab():
    st.header("Journal History")

    entries = get_user_entries(st.session_state.user_id)

    if len(entries) == 0:
        st.info("No journal entries yet. Start by writing your first entry!")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        search_text = st.text_input("Search entries")

    with col2:
        sentiment_filter = st.selectbox(
            "Filter by sentiment",
            ["All", "POSITIVE", "NEGATIVE", "NEUTRAL", "UNKNOWN"]
        )

    filtered_entries = entries

    if search_text.strip():
        filtered_entries = [
            entry for entry in filtered_entries
            if search_text.lower() in str(entry[1]).lower()
        ]

    if sentiment_filter != "All":
        filtered_entries = [
            entry for entry in filtered_entries
            if str(entry[3]).upper() == sentiment_filter
        ]

    if st.button("Export to PDF"):
        pdf_data = create_pdf(filtered_entries, st.session_state.username)

        st.download_button(
            label="Download PDF",
            data=pdf_data,
            file_name=(
                f"mental_health_journal_"
                f"{datetime.now().strftime('%Y%m%d')}.pdf"
            ),
            mime="application/pdf"
        )

    if len(filtered_entries) == 0:
        st.info("No entries match your filters.")
        return

    for date, entry_text, emotion, sentiment, confidence in filtered_entries:
        try:
            display_date = datetime.strptime(
                date, "%Y-%m-%d"
            ).strftime("%B %d, %Y")
        except ValueError:
            display_date = str(date)

        with st.expander(
            f"{display_date} - {emotion} ({sentiment})"
        ):
            st.write(entry_text)

            confidence_text = (
                f"{float(confidence) * 100:.1f}%"
                if confidence is not None else "N/A"
            )

            st.caption(
                f"Emotion: {emotion} | "
                f"Sentiment: {sentiment} | "
                f"Model confidence: {confidence_text}"
            )