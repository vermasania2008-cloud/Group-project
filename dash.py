from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="EduSearch AI",
    page_icon=":material/dashboard:",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = Path(__file__).parent / "style.css"
if css_path.exists():
    st.markdown(
        f"<style>{css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )
else:
    st.error(f"CSS file not found: {css_path}")

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <span class="material-symbols-outlined brand-icon">school</span>
            <div class="sidebar-title">EDUSEARCH AI</div>
        </div>
        <div class="sidebar-subtitle">Smart Practice. Better Results.</div>
        """,
        unsafe_allow_html=True,
    )

    st.page_link("dash.py", label="Dashboard", icon=":material/dashboard:")
    st.page_link("pages/que.py", label="Question Paper Analyzer", icon=":material/document_scanner:")
    st.page_link("pages/ai.py", label="AI Assistant", icon=":material/psychology:")

    papers_analyzed = st.session_state.get("papers_analyzed", 0)
    questions_analyzed = st.session_state.get("questions_analyzed", 0)
    topics_detected = st.session_state.get("topics_detected", 0)

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
    '<div class="section-heading"><span class="material-symbols-outlined">waving_hand</span><span>Welcome back</span></div>',
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
    st.metric("Today's Achievement", f"{questions_analyzed} questions")
with col6:
    st.metric("AI Assistant", "Available")
with col7:
    st.metric("History", f"{papers_analyzed} papers")

