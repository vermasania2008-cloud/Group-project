import os
import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import streamlit as st
from google import genai

from auth import auth_gate, render_app_sidebar

st.set_page_config(
    page_title="AI Timetable Maker",
    page_icon=":material/calendar_month:",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = Path(__file__).resolve().with_name("timetable.css")
if css_path.exists():
    st.markdown(
        f"<style>{css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )

auth_gate()
render_app_sidebar()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "chat_history.db"


def load_env_file(path):
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key not in os.environ and value:
            os.environ[key] = value


def get_api_keys():
    keys = []
    for key_name in ["GEMINI_API_KEY"] + [f"GEMINI_API_KEY_{index}" for index in range(2, 11)]:
        value = os.getenv(key_name, "").strip()
        if value and value not in keys:
            keys.append(value)
    return keys


load_env_file(BASE_DIR / ".env")
API_KEYS = get_api_keys()


def save_timetable(file_name, available_time, answer):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 0,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            deleted INTEGER DEFAULT 0
        )
        """
    )
    user = st.session_state.get("auth_user") or {}
    now = datetime.now()
    conn.execute(
        """
        INSERT INTO chats (user_id, question, answer, date, time, deleted)
        VALUES (?, ?, ?, ?, ?, 0)
        """,
        (
            user.get("id", 0),
            f"Timetable: {file_name} ({available_time})",
            answer,
            now.strftime("%d-%m-%Y"),
            now.strftime("%I:%M %p"),
        ),
    )
    conn.commit()
    conn.close()


def generate_timetable(file_bytes, file_name, available_time):
    prompt = (
        f"AVAILABLE STUDY TIME: {available_time}\n"
        "TASK: Create a detailed study timetable from the uploaded PDF.\n\n"
        "STRICT RULES:\n"
        "- Return a timetable only; do not summarize or explain the PDF.\n"
        "- Use only topics that actually appear in the PDF.\n"
        "- Fit every block inside the available time with exact durations.\n"
        "- Use realistic 25-90 minute blocks with short breaks.\n"
        "- Include priority order, active recall, practice questions, error review, "
        "and final revision.\n\n"
        "FORMAT:\n"
        "# Detailed Study Timetable\n"
        "One line for total time and assumption.\n"
        "| Time block | Duration | PDF topic | Exact study task | Expected output |\n"
        "|---|---:|---|---|---|\n"
        "Then include Priority order and Final checklist.\n"
        "Do not add a PDF summary or general explanation."
    )
    last_error = None

    for api_key in API_KEYS:
        temp_path = BASE_DIR / f".timetable_{uuid4().hex}_{Path(file_name).name}"
        try:
            temp_path.write_bytes(file_bytes)
            client = genai.Client(api_key=api_key)
            gemini_file = client.files.upload(file=str(temp_path))
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[gemini_file, prompt],
                config={
                    "system_instruction": (
                        "You are a strict academic timetable generator. Return only a detailed timetable "
                        "grounded in the uploaded PDF. Never invent topics or summarize the document."
                    ),
                    "temperature": 0.2,
                    "max_output_tokens": 2200,
                },
            )
            if response.text:
                return response.text.strip()
            last_error = "The AI returned an empty timetable."
        except Exception as error:
            last_error = error
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass

    return f"Unable to create the timetable: {last_error or 'No valid API key was available.'}"


st.markdown(
    """
    <div class="ai-header-card">
        <div class="ai-header-badge"><span class="material-symbols-outlined">calendar_month</span> AI study planner</div>
        <div class="ai-header-row">
            <span class="material-symbols-outlined ai-title-icon">event_note</span>
            <h1>Timetable Maker</h1>
        </div>
        <p class="ai-subtitle">Upload your study material, tell us your available time, and get a focused plan.</p>
        <div class="ai-status-row">
            <span class="ai-status-pill"><span class="material-symbols-outlined">schedule</span> Time-aware</span>
            <span class="ai-status-pill"><span class="material-symbols-outlined">target</span> Topic-focused</span>
            <span class="ai-status-pill"><span class="material-symbols-outlined">bolt</span> Actionable</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not API_KEYS:
    st.error("Gemini API key not found. Add GEMINI_API_KEY to pages/.env.")
    st.stop()

left_col, right_col = st.columns([1.05, 0.95], gap="large")
with left_col:
    st.markdown("### 1. Upload your PDF")
    uploaded_file = st.file_uploader(
        "Choose a study PDF",
        type=["pdf"],
        help="Use a syllabus, notes, textbook chapter, or question paper.",
    )
    if uploaded_file:
        st.success(f"Loaded: {uploaded_file.name}")

with right_col:
    st.markdown("### 2. Set your available time")
    available_time = st.text_input(
        "Available study time",
        placeholder="Example: 3 hours tonight or 45 minutes daily for 5 days",
    )
    st.caption("Include a deadline or preferred break pattern if needed.")

if st.button("Generate detailed timetable", type="primary", icon=":material/auto_awesome:", use_container_width=True):
    if not uploaded_file:
        st.warning("Upload a PDF first.")
    elif not available_time.strip():
        st.warning("Tell me how much study time you have first.")
    else:
        with st.spinner("Building your detailed timetable..."):
            result = generate_timetable(
                uploaded_file.getvalue(),
                uploaded_file.name,
                available_time.strip(),
            )
        st.session_state.timetable_result = result
        save_timetable(uploaded_file.name, available_time.strip(), result)

if "timetable_result" in st.session_state:
    st.markdown(
        """
        <div class="timetable-result-header">
            <span class="material-symbols-outlined">calendar_month</span>
            <div><strong>Your detailed study timetable</strong><small>Saved to AI History</small></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(st.session_state.timetable_result)
