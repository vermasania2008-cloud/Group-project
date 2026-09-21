import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

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
    st.page_link("pages/tda.py", label="Today Achievement", icon=":material/workspace_premium:")
    st.page_link("pages/his.py", label="History", icon=":material/history:")
    

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
    '<div class="section-heading"><span class="material-symbols-outlined">school</span><span>EduSearch AI</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-heading"><span class="material-symbols-outlined">workspace_premium</span><span>Today\'s Achievement Tracker</span></div>',
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

st.divider()
st.subheader("Today's Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total", len(today_data))
col2.metric(
    "Completed",
    len(today_data[today_data["Status"] == "Completed"]),
)
col3.metric(
    "In Progress",
    len(today_data[today_data["Status"] == "In Progress"]),
)
col4.metric(
    "Planned",
    len(today_data[today_data["Status"] == "Planned"]),
)

st.divider()
st.subheader("Today's Achievements")

if today_data.empty:
    st.info("No achievements added today.")
else:
    st.dataframe(
        today_data,
        use_container_width=True,
        hide_index=True,
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