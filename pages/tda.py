import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

from auth import auth_gate, render_logout_button, render_page_link

st.set_page_config(
    page_title="EduSearch AI - Today's Achievements",
    page_icon=":material/workspace_premium:",
    layout="wide",
)

st.markdown(
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,400,0,0" />',
    unsafe_allow_html=True,
)

css_path = Path(__file__).parent / "tda.css"
if css_path.exists():
    st.markdown(
        f"<style>{css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )
else:
    st.error(f"CSS file not found: {css_path}")

auth_gate()

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

    render_page_link("dash.py", label="Dashboard", icon=":material/dashboard:")
    render_page_link("pages/que.py", label="Question Paper Analyzer", icon=":material/document_scanner:")
    render_page_link("pages/ai.py", label="AI Assistant", icon=":material/psychology:")
    render_page_link("pages/timetable.py", label="Timetable Maker", icon=":material/calendar_month:")
    render_page_link("pages/tda.py", label="Today Achievement", icon=":material/workspace_premium:")
    render_page_link("pages/timer.py", label="Study Timer", icon=":material/timer:")
    render_page_link("pages/his.py", label="History", icon=":material/history:")
    render_logout_button()
    

DATA_FILE = Path(__file__).parent / "achievements.csv"
COLUMNS = ["Date", "Achievement", "Category", "Status"]


def load_achievements():
    if DATA_FILE.exists():
        try:
            data = pd.read_csv(DATA_FILE)
            for column in COLUMNS:
                if column not in data.columns:
                    data[column] = ""
            return data[COLUMNS]
        except Exception:
            return pd.DataFrame(columns=COLUMNS)

    return pd.DataFrame(columns=COLUMNS)


def save_achievements(data):
    data.to_csv(DATA_FILE, index=False)


st.markdown(
    """
    <div class="achievement-hero">
        <div class="achievement-hero-copy">
            <div class="achievement-kicker"><span class="material-symbols-outlined">workspace_premium</span> Study rewards</div>
            <h1>Achievement Tracker</h1>
            <p>Celebrate your progress, build momentum, and let AI-powered milestones keep you motivated.</p>
        </div>
        <div class="achievement-hero-badge">
            <span class="material-symbols-outlined">bolt</span>
            <span>Level Up</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("Track your daily learning, study, and personal achievements.")

today = str(date.today())
data = load_achievements()

with st.form("achievement_form", clear_on_submit=True):
    achievement = st.text_input(
        "What did you achieve today?",
        placeholder="Example: Completed a Python lesson",
    )

    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "Category",
            ["Study", "Research", "Programming", "Assignment", "Personal", "Other"],
        )

    with col2:
        status = st.selectbox(
            "Status",
            ["Completed", "In Progress", "Planned"],
        )

    submitted = st.form_submit_button(
        "Add Achievement",
        use_container_width=True,
        icon=":material/add_circle:",
    )

if submitted:
    if achievement.strip():
        new_row = pd.DataFrame(
            [{
                "Date": today,
                "Achievement": achievement.strip(),
                "Category": category,
                "Status": status,
            }]
        )

        data = pd.concat([data, new_row], ignore_index=True)
        save_achievements(data)

        st.success("Achievement added successfully!")
        st.rerun()
    else:
        st.warning("Please enter an achievement.")

today_data = data[data["Date"].astype(str) == today]

completed_count = len(today_data[today_data["Status"] == "Completed"])
in_progress_count = len(today_data[today_data["Status"] == "In Progress"])
planned_count = len(today_data[today_data["Status"] == "Planned"])

progress_score = min(100, int((completed_count * 100) / max(1, len(today_data) or 1)))

st.markdown("---")
st.subheader("Today's Summary")

summary_cols = st.columns(4)
with summary_cols[0]:
    st.metric("Total", len(today_data))
with summary_cols[1]:
    st.metric("Completed", completed_count)
with summary_cols[2]:
    st.metric("In Progress", in_progress_count)
with summary_cols[3]:
    st.metric("Planned", planned_count)

reward_banner = "✨ Momentum is building! Keep going!" if completed_count > 0 else "🚀 Start your first streak today."
st.markdown(f"<div class='reward-banner'>{reward_banner}</div>", unsafe_allow_html=True)

progress_col, insight_col = st.columns([2, 1])
with progress_col:
    st.markdown(
        f"""
        <div class="progress-card">
            <div class="progress-head">
                <span>Daily progress</span>
                <strong>{progress_score}%</strong>
            </div>
            <div class="progress-bar"><div class="progress-fill" style="width: {progress_score}%"></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with insight_col:
    ai_note = "Strong performance today." if completed_count >= 2 else "A few small wins can unlock momentum."
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">AI insight</div>
            <div class="insight-text">{ai_note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")
st.subheader("Today's Achievements")

if today_data.empty:
    st.info("No achievements added today. Start small and build your momentum.")
else:
    card_cols = st.columns(3)
    for idx, row in enumerate(today_data.to_dict("records")):
        with card_cols[idx % 3]:
            badge = row["Status"]
            status_class = "status-complete" if badge == "Completed" else "status-progress" if badge == "In Progress" else "status-planned"
            st.markdown(
                f"""
                <div class="achievement-card {status_class}">
                    <div class="achievement-card-top">
                        <span class="material-symbols-outlined">workspace_premium</span>
                        <span class="achievement-badge">{row['Category']}</span>
                    </div>
                    <div class="achievement-title">{row['Achievement']}</div>
                    <div class="achievement-status">{badge}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if st.button(
        "Delete Today's Achievements",
        type="secondary",
        icon=":material/delete:",
    ):
        data = data[data["Date"].astype(str) != today]
        save_achievements(data)

        st.success("Today's achievements deleted.")
        st.rerun()

st.caption(f"EduSearch AI • Date: {today}")