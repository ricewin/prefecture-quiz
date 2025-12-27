import streamlit as st
from streamlit.navigation.page import StreamlitPage


def navigation() -> None:
    pages: dict[str, list[StreamlitPage]] = {
        "Contents": [
            st.Page(
                "pages/quiz.py",
                title="Quiz",
                icon=":material/stadia_controller:",
            ),
            st.Page(
                "pages/study.py",
                title="Study",
                icon=":material/wand_shine:",
            ),
        ],
        # "Resources": [
        #     st.Page("pages/learn.py", title="Learn about me"),
        #     st.Page("pages/overview.py", title="Overview"),
        # ],
    }

    pg: StreamlitPage = st.navigation(pages)
    pg.run()


def page_config() -> None:
    TITLE = "都道府県クイズ"

    st.set_page_config(
        page_title=TITLE,
        page_icon=":material/captive_portal:",
        layout="wide",
    )


def footer() -> None:
    with st.sidebar:
        st.caption(f"*Streamlit Ver. {st.__version__}*")
