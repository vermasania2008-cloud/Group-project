import hashlib
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
AUTH_DB_PATH = BASE_DIR / "auth.db"


def get_auth_connection():
    conn = sqlite3.connect(AUTH_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_auth_db():
    conn = get_auth_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()


def register_user(username: str, email: str, password: str):
    username = (username or "").strip()
    email = (email or "").strip().lower()
    password = (password or "").strip()

    if len(username) < 3:
        return False, "Username must be at least 3 characters long."

    if "@" not in email or "." not in email:
        return False, "Please enter a valid email address."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    conn = get_auth_connection()

    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)",
            (username, email),
        ).fetchone()

        if existing:
            return False, "This username or email is already registered."

        conn.execute(
            """
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (username, email, hash_password(password), datetime.utcnow().isoformat()),
        )
        conn.commit()
        return True, "Account created successfully."

    except sqlite3.Error as exc:
        return False, f"Unable to create account: {exc}"

    finally:
        conn.close()


def authenticate_user(identifier: str, password: str):
    identifier = (identifier or "").strip()
    password = (password or "").strip()

    if not identifier or not password:
        return None

    conn = get_auth_connection()
    user = conn.execute(
        """
        SELECT * FROM users
        WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)
        """,
        (identifier, identifier),
    ).fetchone()
    conn.close()

    if not user:
        return None

    if user["password_hash"] == hash_password(password):
        return dict(user)

    return None


def is_authenticated():
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None
    return st.session_state.auth_user is not None


def create_auth_session(user_id: int):
    token = secrets.token_urlsafe(32)
    conn = get_auth_connection()
    conn.execute(
        "INSERT INTO auth_sessions (token, user_id, created_at) VALUES (?, ?, ?)",
        (token, user_id, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
    st.query_params["auth_token"] = token


def restore_auth_session():
    token = st.query_params.get("auth_token")
    if not token:
        return

    conn = get_auth_connection()
    user = conn.execute(
        """
        SELECT users.*
        FROM auth_sessions
        JOIN users ON users.id = auth_sessions.user_id
        WHERE auth_sessions.token = ?
        """,
        (token,),
    ).fetchone()
    conn.close()

    if user:
        st.session_state.auth_user = dict(user)
    else:
        st.query_params.pop("auth_token", None)


def render_page_link(path: str, **kwargs):
    token = st.query_params.get("auth_token")
    query_params = {"auth_token": token} if token else None
    st.page_link(path, query_params=query_params, **kwargs)


def render_app_sidebar():
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
        render_page_link(
            "pages/que.py",
            label="Question Paper Analyzer",
            icon=":material/document_scanner:",
        )
        render_page_link("pages/ai.py", label="AI Assistant", icon=":material/psychology:")
        render_page_link(
            "pages/timetable.py",
            label="Timetable Maker",
            icon=":material/calendar_month:",
        )
        render_page_link(
            "pages/tda.py",
            label="Today Achievement",
            icon=":material/workspace_premium:",
        )
        render_page_link("pages/timer.py", label="Study Timer", icon=":material/timer:")
        render_page_link("pages/his.py", label="History", icon=":material/history:")
        render_logout_button()


def logout_user():
    token = st.query_params.get("auth_token")
    if token:
        conn = get_auth_connection()
        conn.execute("DELETE FROM auth_sessions WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        st.query_params.pop("auth_token", None)
    st.session_state.pop("auth_user", None)


def render_logout_button():
    if is_authenticated():
        if st.sidebar.button("Logout", icon=":material/logout:"):
            logout_user()
            st.rerun()


def auth_gate():
    init_auth_db()
    restore_auth_session()

    if is_authenticated():
        return st.session_state.auth_user

    st.markdown(
        """
        <style>
            :root {
                --auth-bg: #effaf4;
                --auth-panel: rgba(255,255,255,0.9);
                --auth-border: rgba(9,104,70,0.16);
                --auth-green: #087f52;
                --auth-green-deep: #075338;
                --auth-text: #173b35;
                --auth-muted: #66827a;
            }

            .stApp {
                background:
                    radial-gradient(circle at 9% 12%, rgba(71, 213, 151, 0.18), transparent 22rem),
                    radial-gradient(circle at 92% 86%, rgba(250, 193, 75, 0.16), transparent 18rem),
                    linear-gradient(135deg, #f9fdf9 0%, var(--auth-bg) 100%) !important;
            }

            [data-testid="stAppViewContainer"] {
                background: transparent !important;
            }

            [data-testid="stAppViewContainer"] > .main .block-container {
                max-width: 1180px;
                padding: 3.5rem 2rem 4rem;
            }

            .login-shell {
                position: relative;
                display: flex;
                align-items: center;
                gap: 2.5rem;
                min-height: 520px;
                padding: 2.6rem;
                overflow: hidden;
                border: 1px solid rgba(9,104,70,0.14);
                border-radius: 32px;
                background: rgba(255,255,255,0.52);
                box-shadow: 0 26px 70px rgba(18, 75, 55, 0.12);
                animation: authRise 0.7s ease-out both;
            }

            [data-testid="stHorizontalBlock"]:has(.login-brand-panel) {
                position: relative;
                align-items: stretch;
                gap: 2.5rem;
                margin: 1.5rem 0 2rem;
                padding: 2.6rem;
                overflow: hidden;
                border: 1px solid rgba(9,104,70,0.14);
                border-radius: 32px;
                background: rgba(255,255,255,0.52);
                box-shadow: 0 26px 70px rgba(18, 75, 55, 0.12);
                animation: authRise 0.7s ease-out both;
            }

            [data-testid="stHorizontalBlock"]:has(.login-brand-panel)::before,
            [data-testid="stHorizontalBlock"]:has(.login-brand-panel)::after {
                position: absolute;
                content: "";
                border-radius: 50%;
                pointer-events: none;
            }

            [data-testid="stHorizontalBlock"]:has(.login-brand-panel)::before {
                width: 22rem;
                height: 22rem;
                right: -9rem;
                top: -10rem;
                background: rgba(70, 212, 149, 0.16);
            }

            [data-testid="stHorizontalBlock"]:has(.login-brand-panel)::after {
                width: 11rem;
                height: 11rem;
                left: -5rem;
                bottom: -5rem;
                background: rgba(250, 193, 75, 0.15);
            }

            [data-testid="column"]:has(.login-form-panel) {
                position: relative;
                z-index: 1;
                padding: 1.35rem;
                border: 1px solid rgba(9,104,70,0.14);
                border-radius: 24px;
                background: rgba(255,255,255,0.72);
                box-shadow: 0 14px 32px rgba(10, 76, 65, 0.08);
            }

            .login-shell::before,
            .login-shell::after {
                position: absolute;
                content: "";
                border-radius: 50%;
                pointer-events: none;
            }

            .login-shell::before {
                width: 22rem;
                height: 22rem;
                right: -9rem;
                top: -10rem;
                background: rgba(70, 212, 149, 0.16);
            }

            .login-shell::after {
                width: 11rem;
                height: 11rem;
                left: -5rem;
                bottom: -5rem;
                background: rgba(250, 193, 75, 0.15);
            }

            .login-brand-panel {
                position: relative;
                z-index: 1;
                flex: 1 1 48%;
                min-height: 360px;
                padding: 2.2rem;
                overflow: hidden;
                border-radius: 24px;
                color: white;
                background: linear-gradient(145deg, rgba(6, 112, 71, 0.98), rgba(5, 72, 48, 0.98));
                box-shadow: 0 20px 36px rgba(5, 83, 56, 0.2);
            }

            .login-brand-panel::after {
                position: absolute;
                right: -2.5rem;
                bottom: -4rem;
                width: 14rem;
                height: 14rem;
                border: 1px solid rgba(255,255,255,0.23);
                border-radius: 50%;
                content: "";
            }

            .login-brand-mark {
                display: inline-grid;
                place-items: center;
                width: 3.3rem;
                height: 3.3rem;
                margin-bottom: 4.5rem;
                border: 1px solid rgba(255,255,255,0.24);
                border-radius: 16px;
                background: rgba(255,255,255,0.14);
                font-size: 1.65rem;
                box-shadow: 0 10px 22px rgba(0,0,0,0.12);
            }

            .login-brand-panel h1 {
                max-width: 26rem;
                margin: 0 0 0.9rem !important;
                color: white !important;
                font-size: clamp(2.2rem, 5vw, 3.7rem) !important;
                line-height: 0.98 !important;
            }

            .login-brand-panel p {
                max-width: 26rem;
                margin: 0;
                color: rgba(255,255,255,0.77) !important;
                font-size: 1rem;
                line-height: 1.65;
            }

            .login-brand-points {
                display: flex;
                flex-wrap: wrap;
                gap: 0.55rem;
                margin-top: 2rem;
            }

            .login-brand-points span {
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                padding: 0.45rem 0.65rem;
                border: 1px solid rgba(255,255,255,0.18);
                border-radius: 999px;
                background: rgba(255,255,255,0.1);
                color: rgba(255,255,255,0.9);
                font-size: 0.72rem;
                font-weight: 750;
            }

            .login-form-panel {
                position: relative;
                z-index: 1;
                flex: 1 1 42%;
                min-width: 0;
            }

            .login-form-panel h2 {
                margin: 0 0 0.35rem !important;
                color: var(--auth-green-deep) !important;
                font-size: 1.7rem !important;
            }

            .login-form-panel > p {
                margin: 0 0 1.25rem;
                color: var(--auth-muted);
            }

            .login-form-panel {
                padding-top: 1.2rem;
            }

            .login-form-panel div[data-testid="stForm"] {
                padding: 1.35rem 1.25rem 0.9rem;
            }

            .login-form-panel div[data-testid="stTabs"] {
                margin-top: 0.8rem;
            }

            .login-form-panel div[data-testid="stTabList"] {
                gap: 0.35rem;
                padding: 0.3rem;
                border-radius: 14px;
                background: rgba(9,104,70,0.07);
            }

            .login-form-panel div[data-testid="stTab"] {
                border: 0;
                border-radius: 10px;
                color: var(--auth-muted);
                font-weight: 750;
                padding: 0.55rem 0.7rem;
            }

            .login-form-panel div[data-testid="stTab"][aria-selected="true"] {
                background: white;
                color: var(--auth-green-deep);
                box-shadow: 0 4px 12px rgba(18, 75, 55, 0.1);
            }

            div[data-testid="stForm"] {
                background: var(--auth-panel);
                border: 1px solid var(--auth-border);
                border-radius: 22px;
                padding: 1.2rem 1.15rem 0.9rem;
                box-shadow: 0 14px 32px rgba(10, 76, 65, 0.08);
            }

            div[data-testid="stTabList"] {
                gap: 0.5rem;
                margin-bottom: 0.9rem;
            }

            div[data-testid="stTab"] {
                background: rgba(255,255,255,0.68);
                border: 1px solid rgba(6,122,76,0.12);
                border-radius: 12px 12px 0 0;
                color: var(--auth-muted);
                font-weight: 700;
                padding: 0.6rem 1rem;
            }

            div[data-testid="stTab"][aria-selected="true"] {
                background: linear-gradient(135deg, rgba(218,250,240,0.9), rgba(255,255,255,0.82));
                border-color: rgba(6,122,76,0.2);
                color: var(--auth-green-deep);
            }

            div.stTextInput > label,
            div.stPasswordInput > label,
            div.stSelectbox > label {
                color: var(--auth-text) !important;
                font-weight: 700 !important;
            }

            .stTextInput input,
            .stPasswordInput input,
            .stTextInput textarea,
            .stPasswordInput textarea,
            .stSelectbox select,
            .stTextInput > div > div > input,
            .stPasswordInput > div > div > input {
                color: #111111 !important;
                background: rgba(255,255,255,0.92) !important;
                border: 1px solid rgba(6,122,76,0.18) !important;
                border-radius: 12px !important;
                box-shadow: none !important;
            }

            .stTextInput input::placeholder,
            .stPasswordInput input::placeholder {
                color: #667d78 !important;
                opacity: 1;
            }

            .stTextInput input:focus,
            .stPasswordInput input:focus,
            .stTextInput textarea:focus,
            .stPasswordInput textarea:focus,
            .stSelectbox select:focus {
                border-color: rgba(6,122,76,0.52) !important;
                box-shadow: 0 0 0 0.18rem rgba(37,209,139,0.18) !important;
            }

            div[data-testid="stInfo"],
            div[data-testid="stError"],
            div[data-testid="stSuccess"] {
                background: rgba(255,255,255,0.75);
                border: 1px solid rgba(6,122,76,0.12);
                border-radius: 14px;
                color: var(--auth-text);
            }

            .stButton > button {
                background: linear-gradient(135deg, var(--auth-green), var(--auth-green-deep));
                color: white !important;
                border: none !important;
                border-radius: 12px !important;
                font-weight: 800 !important;
                padding: 0.7rem 1.2rem !important;
                box-shadow: 0 12px 24px rgba(6,122,76,0.18);
            }

            .stButton > button:hover {
                filter: brightness(1.04);
                transform: translateY(-1px);
                box-shadow: 0 15px 28px rgba(6,122,76,0.24);
            }

            @keyframes authRise {
                from { opacity: 0; transform: translateY(18px); }
                to { opacity: 1; transform: translateY(0); }
            }

            @media (max-width: 760px) {
                [data-testid="stAppViewContainer"] > .main .block-container {
                    padding: 1.5rem 0.85rem 2.5rem;
                }

                .login-shell {
                    display: block;
                    min-height: auto;
                    padding: 1rem;
                    border-radius: 24px;
                }

                [data-testid="stHorizontalBlock"]:has(.login-brand-panel) {
                    display: block;
                    margin: 0.5rem 0 1rem;
                    padding: 1rem;
                    border-radius: 24px;
                }

                [data-testid="column"]:has(.login-form-panel) {
                    margin-top: 1rem;
                    padding: 1rem;
                }

                .login-brand-panel {
                    min-height: auto;
                    margin-bottom: 1rem;
                    padding: 1.5rem;
                }

                .login-brand-mark {
                    margin-bottom: 2.5rem;
                }

                .login-brand-panel h1 {
                    font-size: 2.35rem !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left_panel, right_panel = st.columns([1.05, 0.95], gap="large")

    with left_panel:
        st.markdown(
            """
            <div class="login-brand-panel">
                <div class="login-brand-mark"><span class="material-symbols-outlined">auto_awesome</span></div>
                <h1>Make every study session count.</h1>
                <p>Your focused academic workspace for smarter revision, AI-powered support, and visible progress.</p>
                <div class="login-brand-points">
                    <span><span class="material-symbols-outlined">psychology</span> AI support</span>
                    <span><span class="material-symbols-outlined">insights</span> Track progress</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_panel:
        st.markdown(
            """
            <div class="login-form-panel">
                <h2>Welcome back</h2>
                <p>Sign in to continue your learning journey.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        login_tab, signup_tab = st.tabs(["Login", "Create account"])

        with login_tab:
            with st.form("login_form", clear_on_submit=False):
                username_or_email = st.text_input("Username or email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)

                if submitted:
                    user = authenticate_user(username_or_email, password)
                    if user:
                        st.session_state.auth_user = user
                        create_auth_session(user["id"])
                        st.success(f"Welcome back, {user['username']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username/email or password.")

        with signup_tab:
            with st.form("signup_form", clear_on_submit=False):
                username = st.text_input("Username")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm password", type="password")
                submitted = st.form_submit_button("Create account", use_container_width=True)

                if submitted:
                    if password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        ok, message = register_user(username, email, password)
                        if ok:
                            user = authenticate_user(username, password)
                            if user:
                                st.session_state.auth_user = user
                                create_auth_session(user["id"])
                                st.success("Account created successfully. You are now logged in.")
                                st.rerun()
                        else:
                            st.error(message)

    st.stop()
    return None
