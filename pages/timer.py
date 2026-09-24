import sqlite3
import time
from datetime import date, datetime
from pathlib import Path

import streamlit as st

from auth import auth_gate, render_logout_button, render_page_link

st.set_page_config(
    page_title="EduSearch AI | Focus Timer",
    page_icon=":material/timer:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,400,0,0" />',
    unsafe_allow_html=True,
)

auth_gate()


# ============================================================
# CONFIGURATION
# ============================================================

DB_NAME = "chat_history.db"
DEFAULT_FOCUS_MINUTES = 25
DEFAULT_BREAK_MINUTES = 5
MIN_TIMER_MINUTES = 1
MAX_TIMER_MINUTES = 180

#============================================================
#   SIDEBAR
#============================================================

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

css_path = Path(__file__).parent.parent / "style.css"
if css_path.exists():
    st.markdown(
        f"<style>{css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )
else:
    st.error(f"CSS file not found: {css_path}")

   

# ============================================================
# DATABASE
# Keeps timer history separate from AI Assistant / app history.
# The table is stored in the same SQLite database, but this page
# is the only place that reads/writes these focus records.
# ============================================================

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def create_timer_table():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                duration INTEGER NOT NULL,
                session_type TEXT NOT NULL DEFAULT 'Focus',
                date TEXT NOT NULL,
                time TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_focus_session(task: str, duration: int):
    task = (task or "Untitled Focus Session").strip()
    if not task:
        task = "Untitled Focus Session"

    now = datetime.now()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO focus_sessions
            (task, duration, session_type, date, time)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                task[:120],
                int(duration),
                "Focus",
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M"),
            ),
        )
        conn.commit()


def get_today_sessions():
    today = date.today().strftime("%Y-%m-%d")

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, task, duration, time
            FROM focus_sessions
            WHERE date = ? AND session_type = 'Focus'
            ORDER BY id DESC
            """,
            (today,),
        ).fetchall()

    return rows


def get_today_focus_minutes():
    today = date.today().strftime("%Y-%m-%d")

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(SUM(duration), 0) AS total
            FROM focus_sessions
            WHERE date = ? AND session_type = 'Focus'
            """,
            (today,),
        ).fetchone()

    return int(row["total"] if row else 0)


# ============================================================
# SESSION STATE
# ============================================================

def initialize_timer():
    defaults = {
        "timer_running": False,
        "timer_mode": "Focus",
        "remaining_seconds": DEFAULT_FOCUS_MINUTES * 60,
        "focus_minutes": DEFAULT_FOCUS_MINUTES,
        "break_minutes": DEFAULT_BREAK_MINUTES,
        "task_name": "Reading",
        "end_time": None,
        "session_total_seconds": DEFAULT_FOCUS_MINUTES * 60,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================
# TIMER ENGINE
# Uses an absolute end timestamp instead of subtracting one
# second on every rerun. This avoids timer drift.
# ============================================================

def current_total_seconds():
    if st.session_state.timer_mode == "Focus":
        return st.session_state.focus_minutes * 60
    return st.session_state.break_minutes * 60


def sync_remaining_time():
    if not st.session_state.timer_running:
        return

    end_time = st.session_state.end_time
    if end_time is None:
        st.session_state.timer_running = False
        return

    remaining = max(0, int(end_time - time.time()))
    st.session_state.remaining_seconds = remaining

    if remaining > 0:
        return

    finish_current_session()


def finish_current_session():
    mode = st.session_state.timer_mode

    st.session_state.timer_running = False
    st.session_state.end_time = None
    st.session_state.remaining_seconds = 0

    if mode == "Focus":
        # Only completed focus sessions are written to history.
        save_focus_session(
            st.session_state.task_name,
            st.session_state.focus_minutes,
        )

        st.session_state.timer_mode = "Break"
        st.session_state.session_total_seconds = (
            st.session_state.break_minutes * 60
        )
        st.session_state.remaining_seconds = (
            st.session_state.break_minutes * 60
        )
    else:
        st.session_state.timer_mode = "Focus"
        st.session_state.session_total_seconds = (
            st.session_state.focus_minutes * 60
        )
        st.session_state.remaining_seconds = (
            st.session_state.focus_minutes * 60
        )


def start_timer():
    sync_remaining_time()

    if st.session_state.remaining_seconds <= 0:
        st.session_state.remaining_seconds = current_total_seconds()

    st.session_state.session_total_seconds = (
        st.session_state.remaining_seconds
        if st.session_state.remaining_seconds > 0
        else current_total_seconds()
    )
    st.session_state.end_time = time.time() + st.session_state.remaining_seconds
    st.session_state.timer_running = True


def pause_timer():
    sync_remaining_time()

    if st.session_state.timer_running:
        return

    # sync_remaining_time() already calculates the remaining time
    # when the timer is running, so nothing else is needed here.


def reset_timer():
    st.session_state.timer_running = False
    st.session_state.end_time = None
    st.session_state.session_total_seconds = current_total_seconds()
    st.session_state.remaining_seconds = current_total_seconds()


def switch_mode_without_saving():
    """Skip the current mode without creating a history record."""
    st.session_state.timer_running = False
    st.session_state.end_time = None

    if st.session_state.timer_mode == "Focus":
        st.session_state.timer_mode = "Break"
        st.session_state.session_total_seconds = (
            st.session_state.break_minutes * 60
        )
        st.session_state.remaining_seconds = (
            st.session_state.break_minutes * 60
        )
    else:
        st.session_state.timer_mode = "Focus"
        st.session_state.session_total_seconds = (
            st.session_state.focus_minutes * 60
        )
        st.session_state.remaining_seconds = (
            st.session_state.focus_minutes * 60
        )


def apply_timer_settings(task: str, focus: int, break_time: int):
    task = (task or "").strip()
    if not task:
        task = "Untitled Focus Session"

    st.session_state.task_name = task[:120]
    st.session_state.focus_minutes = focus
    st.session_state.break_minutes = break_time

    # Settings affect the next fresh timer. Never silently modify a
    # timer that is currently running.
    if not st.session_state.timer_running:
        st.session_state.session_total_seconds = current_total_seconds()
        st.session_state.remaining_seconds = current_total_seconds()


# ============================================================
# FORMATTING + CSS
# ============================================================

def format_time(total_seconds: int) -> str:
    total_seconds = max(0, int(total_seconds))
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def format_minutes(total_minutes: int) -> str:
    total_minutes = int(total_minutes)

    hours, minutes = divmod(total_minutes, 60)

    if hours and minutes:
        return f"{hours}h {minutes}m"
    if hours:
        return f"{hours}h"
    return f"{minutes}m"


def get_progress_angle() -> float:
    total = max(1, st.session_state.session_total_seconds)
    remaining = max(0, st.session_state.remaining_seconds)
    progress = min(1, max(0, remaining / total))
    return 360 * progress


def build_css():
    return """
    <style>

    /* ---------- Page ---------- */

    .stApp {
        background:
            radial-gradient(circle at 8% 0%, rgba(45, 212, 191, 0.15), transparent 28%),
            radial-gradient(circle at 92% 8%, rgba(6, 122, 76, 0.12), transparent 24%),
            #f1fbf8;
    }

    .main .block-container {
        max-width: 1240px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* ---------- Header ---------- */

    .timer-header {
        margin-bottom: 1.4rem;
    }

    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #e0f8ef;
        color: #067a4c;
        border: 1px solid #b8ead8;
        border-radius: 999px;
        padding: 7px 12px;
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .page-title {
        margin: 10px 0 4px 0;
        color: #006033;
        font-size: clamp(2.1rem, 4.2vw, 3.4rem);
        line-height: 1.02;
        letter-spacing: -0.045em;
        font-weight: 850;
    }

    .page-subtitle {
        color: #568087;
        font-size: 1rem;
        max-width: 720px;
        line-height: 1.55;
    }

    /* ---------- Cards ---------- */

    .glass-card {
        background: rgba(255,255,255,0.90);
        border: 1px solid #c7ebe5;
        border-radius: 24px;
        box-shadow: 0 16px 50px rgba(15, 23, 42, 0.07);
    }

    .section-label {
        color: #0f5c41;
        font-size: 0.78rem;
        font-weight: 850;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 9px;
    }

    .muted {
        color: #7eadba;
        font-size: 0.85rem;
    }

    /* ---------- Timer shell ---------- */

    .timer-shell {
        background: linear-gradient(145deg, #064e3b 0%, #0f766e 55%, #073b35 100%);
        border-radius: 30px;
        min-height: 640px;
        padding: 28px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 24px 70px rgba(6, 95, 67, 0.22);
    }

    .timer-shell:before {
        content: "";
        position: absolute;
        width: 340px;
        height: 340px;
        border-radius: 50%;
        background: rgba(52, 211, 153, 0.20);
        filter: blur(70px);
        top: -180px;
        right: -120px;
    }

    .timer-shell:after {
        content: "";
        position: absolute;
        width: 300px;
        height: 300px;
        border-radius: 50%;
        background: rgba(153, 246, 228, 0.14);
        filter: blur(75px);
        bottom: -200px;
        left: -100px;
    }

    .timer-topline {
        position: relative;
        z-index: 2;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 16px;
    }

    .mode-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: #ffffff;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 999px;
        padding: 8px 12px;
        font-size: 0.78rem;
        font-weight: 750;
        backdrop-filter: blur(8px);
    }

    .mode-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #5eead4;
        box-shadow: 0 0 0 5px rgba(94,234,212,0.14);
    }

    .running-pill {
        color: #c7f9e9;
        font-size: 0.76rem;
        font-weight: 750;
    }

    /* ---------- Ring ---------- */

    .timer-area {
        min-height: 495px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        z-index: 2;
    }

    .timer-ring {
        width: min(420px, 72vw);
        aspect-ratio: 1;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        background: conic-gradient(
            #34d399 var(--angle),
            rgba(255,255,255,0.10) var(--angle)
        );
        box-shadow:
            0 0 0 1px rgba(255,255,255,0.06),
            0 18px 70px rgba(0,0,0,0.18);
    }

    .timer-ring:before {
        content: "";
        position: absolute;
        inset: 12px;
        border-radius: 50%;
        background:
            radial-gradient(circle at 35% 22%, rgba(255,255,255,0.08), transparent 32%),
            #073b35;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: inset 0 0 50px rgba(0,0,0,0.28);
    }

    .timer-content {
        position: relative;
        z-index: 2;
        text-align: center;
    }

    .timer-task {
        color: #aab5c7;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 8px;
        max-width: 260px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        margin-left: auto;
        margin-right: auto;
    }

    .clock {
        color: #ffffff;
        font-size: clamp(4rem, 8vw, 6.2rem);
        line-height: 0.95;
        font-weight: 850;
        letter-spacing: -0.055em;
        font-variant-numeric: tabular-nums;
    }

    .clock-help {
        color: #8491a5;
        margin-top: 12px;
        font-size: 0.78rem;
    }

    .timer-status {
        color: #cbd5e1;
        font-size: 0.86rem;
        text-align: center;
        margin-top: 8px;
    }

    /* ---------- Sidebar metrics ---------- */

    .metric-card {
        background: #ffffff;
        border: 1px solid #e7eaf0;
        border-radius: 20px;
        padding: 18px;
        box-shadow: 0 12px 35px rgba(15,23,42,0.05);
        height: 100%;
    }

    .metric-title {
        color: #568087;
        font-size: 0.78rem;
        font-weight: 750;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #0f5c41;
        font-size: 1.9rem;
        line-height: 1;
        font-weight: 850;
        letter-spacing: -0.035em;
    }

    .metric-caption {
        color: #7eadba;
        margin-top: 7px;
        font-size: 0.72rem;
    }

    /* ---------- History ---------- */

    .history-panel {
        background: #ffffff;
        border: 1px solid #e7eaf0;
        border-radius: 24px;
        padding: 20px;
        box-shadow: 0 12px 35px rgba(15,23,42,0.05);
    }

    .history-title {
        color: #0f5c41;
        font-size: 1rem;
        font-weight: 850;
        margin-bottom: 2px;
    }

    .history-subtitle {
        color: #7eadba;
        font-size: 0.78rem;
        margin-bottom: 16px;
    }

    .history-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 13px 0;
        border-bottom: 1px solid #eef1f5;
    }

    .history-item:last-child {
        border-bottom: none;
        padding-bottom: 0;
    }

    .history-left {
        min-width: 0;
    }

    .history-task {
        color: #12343b;
        font-size: 0.86rem;
        font-weight: 750;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 310px;
    }

    .history-time {
        color: #7eadba;
        font-size: 0.72rem;
        margin-top: 3px;
    }

    .history-duration {
        flex-shrink: 0;
        color: #067a4c;
        background: #e0f8ef;
        border: 1px solid #b8ead8;
        border-radius: 999px;
        padding: 5px 9px;
        font-size: 0.72rem;
        font-weight: 850;
    }

    .empty-state {
        text-align: center;
        padding: 28px 10px;
        color: #7eadba;
        font-size: 0.82rem;
    }

    /* ---------- Responsive ---------- */

    @media (max-width: 900px) {
        .timer-shell {
            min-height: 580px;
            padding: 20px;
        }

        .timer-area {
            min-height: 430px;
        }
    }

    @media (max-width: 600px) {
        .main .block-container {
            padding-left: 0.9rem;
            padding-right: 0.9rem;
        }

        .timer-shell {
            border-radius: 22px;
        }

        .timer-topline {
            align-items: flex-start;
        }

        .timer-ring {
            width: min(330px, 82vw);
        }

        .history-task {
            max-width: 185px;
        }
    }

    /* ---------- Streamlit buttons ---------- */

    div.stButton > button {
        min-height: 46px;
        border-radius: 13px;
        font-weight: 800;
        border: 1px solid #b8ead8;
        transition: all 0.15s ease;
    }

    div.stButton > button:hover {
        border-color: #2ca864;
        transform: translateY(-1px);
    }

    /* Primary action */
    .primary-action div.stButton > button {
        background: #ffffff;
        color: #0f5c41;
        border: none;
        box-shadow: 0 12px 24px rgba(0,0,0,0.18);
    }

    /* Dark action row */
    .dark-action div.stButton > button {
        background: rgba(255,255,255,0.07);
        color: #e0f8ef;
        border: 1px solid rgba(255,255,255,0.12);
    }

    /* Remove excess vertical space around grouped controls */
    .compact-control {
        margin-top: -6px;
    }

    </style>
    """


# ============================================================
# UI HELPERS
# ============================================================

def render_header():
    st.markdown(
        """
        <div class="timer-header">
            <div class="eyebrow"><span class="material-symbols-outlined">timer</span> Study Focus System</div>
            <div class="page-title">Pomodoro Focus Timer</div>
            <div class="page-subtitle">
                Turn study time into completed sessions. Set your task, choose your
                focus and break duration, then let the timer track the work for you.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_settings():
    st.markdown('<div class="section-label">Session setup</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([2.1, 1, 1, 1], vertical_alignment="bottom")

    with col1:
        task = st.text_input(
            "Task",
            value=st.session_state.task_name,
            placeholder="e.g. OS chapter 3",
            label_visibility="visible",
        )

    with col2:
        focus = st.number_input(
            "Focus (min)",
            min_value=MIN_TIMER_MINUTES,
            max_value=MAX_TIMER_MINUTES,
            value=int(st.session_state.focus_minutes),
            step=1,
        )

    with col3:
        break_time = st.number_input(
            "Break (min)",
            min_value=MIN_TIMER_MINUTES,
            max_value=60,
            value=int(st.session_state.break_minutes),
            step=1,
        )

    with col4:
        st.markdown('<div class="compact-control">', unsafe_allow_html=True)
        apply_clicked = st.button(
            "Apply settings",
            use_container_width=True,
            key="apply_timer_settings",
            icon=":material/tune:",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if apply_clicked:
        if st.session_state.timer_running:
            st.warning("Pause the timer before changing the active session settings.")
        else:
            apply_timer_settings(task, int(focus), int(break_time))
            st.rerun()


def render_metrics(today_sessions):
    today_minutes = get_today_focus_minutes()
    completed = len(today_sessions)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title"><span class="material-symbols-outlined">local_fire_department</span> Today's focus</div>
                <div class="metric-value">{format_minutes(today_minutes)}</div>
                <div class="metric-caption">Completed focus sessions only</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                        <div class="metric-title"><span class="material-symbols-outlined">task_alt</span> Sessions done</div>
                <div class="metric-value">{completed}</div>
                <div class="metric-caption">Completed today</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_history(today_sessions):
    st.markdown(
        """
        <div class="history-panel">
            <div class="history-title">Today's focus history</div>
            <div class="history-subtitle">
                This list belongs to the timer page only.
            </div>
        """,
        unsafe_allow_html=True,
    )

    if not today_sessions:
        st.markdown(
            """
            <div class="empty-state">
                No completed focus sessions yet.<br>
                Finish your first session and it will appear here automatically.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for row in today_sessions[:12]:
            safe_task = (
                str(row["task"])
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )
            st.markdown(
                f"""
                <div class="history-item">
                        <div class="history-title"><span class="material-symbols-outlined">history</span> Today's focus history</div>
                        <div class="history-task">{safe_task}</div>
                        <div class="history-time">{row["time"]}</div>
                    </div>
                    <div class="history-duration">{int(row["duration"])}m</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# TIMER VIEW
# ============================================================

def render_timer_engine():
    was_running = st.session_state.timer_running
    previous_mode = st.session_state.timer_mode

    sync_remaining_time()

    if (
        was_running
        and previous_mode == "Focus"
        and not st.session_state.timer_running
        and st.session_state.timer_mode == "Break"
    ):
        st.rerun(scope="app")

    mode = st.session_state.timer_mode
    remaining = format_time(st.session_state.remaining_seconds)
    mode_text = "Break Time" if mode == "Break" else "Focus Session"

    if st.session_state.timer_running:
        status_text = "Timer is running"
        action_label = "Pause"
    else:
        status_text = "Ready to continue"
        action_label = "Start break" if mode == "Break" else "Start focus"

    with st.container():
        st.markdown(
            f"<div style='background:linear-gradient(145deg,#064e3b,#0f766e,#073b35);padding:24px;border-radius:24px;max-width:820px;margin:0 auto;'>"
            f"<div style='display:flex;justify-content:space-between;align-items:center;color:white;margin-bottom:20px;'>"
            f"<span style='background:rgba(255,255,255,0.1);padding:8px 12px;border-radius:999px;font-size:12px;font-weight:700;'><span class='material-symbols-outlined' style='font-size:16px;vertical-align:middle;margin-right:5px;'> {'self_improvement' if mode == 'Break' else 'center_focus_strong'} </span>{mode_text}</span>"
            f"<span style='font-size:12px;color:#dbeafe;font-weight:700;'>{status_text}</span>"
            f"</div>"
            f"<div style='display:flex;justify-content:center;align-items:center;min-height:360px;'>"
            f"<div style='width:min(420px,72vw);aspect-ratio:1;border-radius:50%;display:flex;align-items:center;justify-content:center;"
            f"background:conic-gradient(#34d399 {get_progress_angle()}deg, rgba(255,255,255,0.10) {get_progress_angle()}deg);"
            f"box-shadow:0 18px 70px rgba(0,0,0,0.18);position:relative;border:1px solid rgba(255,255,255,0.06);'>"
            f"<div style='position:absolute;inset:12px;border-radius:50%;background:#073b35;border:1px solid rgba(255,255,255,0.08);display:flex;align-items:center;justify-content:center;flex-direction:column;'>"
            f"<div style='font-size:12px;color:#b8c2d5;font-weight:700;margin-bottom:8px;'><span class='material-symbols-outlined' style='font-size:15px;vertical-align:middle;margin-right:4px;'>task_alt</span>{st.session_state.task_name}</div>"
            f"<div style='font-size:clamp(3rem,7vw,5.5rem);color:#fff;font-weight:850;letter-spacing:-0.06em;line-height:1;'>{remaining}</div>"
            f"<div style='font-size:12px;color:#9aa8bd;margin-top:10px;'>{'Stay focused on one task.' if mode == 'Focus' else 'Step away and recharge.'}</div>"
            f"</div>"
            f"</div>"
            f"</div>"
            f"<div style='margin-top:18px;text-align:center;color:#dbeafe;font-size:12px;'>"
            f"{'Focus time will be recorded when the countdown reaches zero.' if mode == 'Focus' else 'The next focus session is ready after your break.'}"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    action1, action2, action3 = st.columns([1.5, 1, 1])

    with action1:
        if st.button(
            action_label,
            use_container_width=True,
            key="main_timer_action",
            icon=":material/pause:" if st.session_state.timer_running else ":material/play_arrow:",
        ):
            if st.session_state.timer_running:
                sync_remaining_time()
                st.session_state.timer_running = False
                st.session_state.end_time = None
            else:
                start_timer()
            st.rerun()

    with action2:
        if st.button(
            "Reset",
            use_container_width=True,
            key="reset_timer",
            icon=":material/restart_alt:",
        ):
            reset_timer()
            st.rerun()

    with action3:
        if st.button(
            "Skip",
            use_container_width=True,
            key="skip_timer",
            help="Skip this mode without saving a focus record.",
            icon=":material/skip_next:",
        ):
            switch_mode_without_saving()
            st.rerun()


# Streamlit fragments allow the timer to refresh once per second
# without rerunning the entire page. A small compatibility fallback
# is included for older Streamlit versions.
if hasattr(st, "fragment"):

    @st.fragment(run_every="1s")
    def run_live_timer():
        render_timer_engine()

else:

    def run_live_timer():
        render_timer_engine()
        if st.session_state.timer_running:
            time.sleep(1)
            st.rerun()


# ============================================================
# MAIN
# ============================================================

def render_timer_view():
    create_timer_table()
    initialize_timer()

    st.markdown(build_css(), unsafe_allow_html=True)

    render_header()

    render_settings()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    today_sessions = get_today_sessions()

    left, right = st.columns([1.85, 0.95], gap="large")

    with left:
        run_live_timer()

    with right:
        render_metrics(today_sessions)

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title"><span class="material-symbols-outlined">tune</span> Current settings</div>
                <div style="color:#0f5c41;font-size:1rem;font-weight:850;">
                    Focus &nbsp;·&nbsp; Break
                </div>
                <div style="margin-top:8px;color:#568087;font-size:0.86rem;">
                    %d min &nbsp; / &nbsp; %d min
                </div>
            </div>
            """
            % (
                st.session_state.focus_minutes,
                st.session_state.break_minutes,
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    render_history(today_sessions)


def main():
    render_timer_view()


if __name__ == "__main__":
    main()

