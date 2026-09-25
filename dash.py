from pathlib import Path

import streamlit as st

from auth import auth_gate, render_app_sidebar

st.set_page_config(
    page_title="Edusearch AI",
    page_icon=":material/dashboard:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,400,0,0" />',
    unsafe_allow_html=True,
)

css_path = Path(__file__).parent / "style.css"
if css_path.exists():
    st.markdown(
        f"<style>{css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )
else:
    st.error(f"CSS file not found: {css_path}")

auth_gate()

render_app_sidebar()

papers_analyzed = st.session_state.get("papers_analyzed", 0)
questions_analyzed = st.session_state.get("questions_analyzed", 0)
topics_detected = st.session_state.get("topics_detected", 0)

user_name = st.session_state.get("auth_user", {}).get("username", "Student")

st.markdown(
    """
    <div class="hero-panel">
        <div class="hero-copy">
            <div class="hero-kicker"><span class="material-symbols-outlined">auto_awesome</span> YOUR STUDY COMMAND CENTER</div>
            <h1>Edusearch AI</h1>
            <p>Turn question papers into a sharper, more confident study plan.</p>
            <div class="hero-status"><span class="status-dot"></span> Analysis workspace ready</div>
        </div>
        <div class="hero-art" aria-hidden="true">
            <span class="material-symbols-outlined hero-art-main">school</span>
            <span class="material-symbols-outlined hero-art-small hero-art-one">insights</span>
            <span class="material-symbols-outlined hero-art-small hero-art-two">bolt</span>
            <span class="hero-orbit"></span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="section-heading"><span class="material-symbols-outlined">waving_hand</span><span>Welcome back, {user_name}</span></div>',
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Papers Analyzed", papers_analyzed)
with col2:
    st.metric("Questions Found", questions_analyzed)
with col3:
    st.metric("Topics Detected", topics_detected)
with col4:
    st.metric("Streak", "Ready")

st.markdown(
    '<div class="section-heading"><span class="material-symbols-outlined">apps</span><span>Quick access</span></div>',
    unsafe_allow_html=True,
)
col5, col6, col7 = st.columns(3)
with col5:
    if st.button(
        "Today's Achievement",
        key="quick_achievement",
        icon=":material/workspace_premium:",
        width="stretch",
    ):
        st.switch_page("pages/tda.py")
    st.caption(f"{questions_analyzed} questions tracked")
with col6:
    if st.button(
        "AI Assistant",
        key="quick_assistant",
        icon=":material/psychology:",
        width="stretch",
    ):
        st.switch_page("pages/ai.py")
    st.caption("Ask, explore, and study")
with col7:
    if st.button(
        "History",
        key="quick_history",
        icon=":material/history:",
        width="stretch",
    ):
        st.switch_page("pages/his.py")
    st.caption(f"{papers_analyzed} papers analyzed")

