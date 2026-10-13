import streamlit as st
from database import init_db
from utils import login_section, check_authentication
from utils import load_model, sidebar_content
from Components.journal_tab import journal_tab
from Components.history_tab import history_tab
from Components.analytics_tab import analytics_tab
from Components.settings_tab import settings_tab


st.set_page_config(
    page_title="MindCare - Mental Health Journal",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    init_db()

    if not check_authentication():
        login_section()
        return

    st.title(
        f"MindCare Journal - Welcome {st.session_state.username}!"
    )

    sentiment_pipeline = load_model()

    tab1, tab2, tab3, tab4 = st.tabs(
        ["New Entry", "History", "Analytics", "Settings"]
    )

    with tab1:
        journal_tab(sentiment_pipeline)

    with tab2:
        history_tab()

    with tab3:
        analytics_tab()

    with tab4:
        settings_tab()

    sidebar_content()


if __name__ == "__main__":
    main()