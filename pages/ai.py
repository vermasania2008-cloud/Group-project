
import streamlit as st
import sqlite3
from datetime import datetime
from google import genai
import os
from pathlib import Path
from uuid import uuid4

from auth import auth_gate, render_logout_button, render_page_link

st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,400,0,0" />',
    unsafe_allow_html=True,
)

css_path = Path(__file__).resolve().with_name("ai.css")
if css_path.exists():
    css = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
else:
    st.error(f"CSS file not found: {css_path}")

auth_gate()


def load_env_file(path):
    """Load simple KEY=VALUE entries without requiring python-dotenv."""
    if not os.path.isfile(path):
        return

    with open(path, encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            clean_key = key.strip()
            clean_value = value.strip().strip("'\"")

            if clean_key.startswith("GEMINI_API_KEY"):
                if clean_key not in os.environ and clean_value:
                    os.environ[clean_key] = clean_value
            elif clean_key not in os.environ:
                os.environ[clean_key] = clean_value


def get_api_keys():
    keys = []
    primary = os.getenv("GEMINI_API_KEY", "").strip()
    if primary:
        keys.append(primary)

    for index in range(2, 11):
        backup = os.getenv(f"GEMINI_API_KEY_{index}", "").strip()
        if backup and backup not in keys:
            keys.append(backup)

    return keys

                               # LOAD ENVIRONMENT VARIABLES
load_env_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

                                # DATABASE
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "chat_history.db")

conn = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)

cursor = conn.cursor()

                                 # CREATE CHAT TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 0,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    deleted INTEGER DEFAULT 0
)
""")

conn.commit()

cursor.execute("PRAGMA table_info(chats)")
columns = [column[1] for column in cursor.fetchall()]
if "user_id" not in columns:
    cursor.execute("ALTER TABLE chats ADD COLUMN user_id INTEGER DEFAULT 0")
    conn.commit()
if "deleted" not in columns:
    cursor.execute("ALTER TABLE chats ADD COLUMN deleted INTEGER DEFAULT 0")
    conn.commit()

                                  # SESSION STATE
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "recent_chat_id" not in st.session_state:
    st.session_state.recent_chat_id = None
                                
                                  # GEMINI API
API_KEYS = get_api_keys()

if not API_KEYS:
    st.markdown(
        """
        <div class="notice-box error-box">
            <span class="material-symbols-outlined">error</span>
            <div>
                <strong>Gemini API key not found.</strong>
                <small>Please add GEMINI_API_KEY and optional backup keys such as GEMINI_API_KEY_2 in your .env file.</small>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

st.markdown(
    """
    <div class="ai-header-card">
        <div class="ai-header-badge">
            <span class="material-symbols-outlined">smart_toy</span>
            AI assistant
        </div>
        <div class="ai-header-row">
            <span class="material-symbols-outlined ai-title-icon">psychology</span>
            <h1>AI Assistant</h1>
        </div>
        <p class="ai-subtitle">Ask anything. Upload a file when you want answers grounded in your document.</p>
        <div class="ai-status-row">
            <span class="ai-status-pill"><span class="material-symbols-outlined">bolt</span> Fast answers</span>
            <span class="ai-status-pill"><span class="material-symbols-outlined">upload_file</span> File-aware</span>
            <span class="ai-status-pill"><span class="material-symbols-outlined">school</span> Academic focus</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


def handle_prompt(question, uploaded_file=None):
    if not question and uploaded_file is None:
        return

    with st.chat_message("user"):
        if question:
            st.markdown(f"<div class='prompt-bubble'>{question}</div>", unsafe_allow_html=True)

        if uploaded_file:
            st.markdown(
                f'<div class="upload-chip"><span class="material-symbols-outlined">attach_file</span>{uploaded_file.name}</div>',
                unsafe_allow_html=True,
            )

    with st.chat_message("assistant"):
        with st.spinner("Reading and analyzing..."):
            answer = generate_answer(question, uploaded_file)

        st.markdown(f"<div class='assistant-answer'>{answer}</div>", unsafe_allow_html=True)

    display_question = question

    if not display_question and uploaded_file:
        display_question = f"📎 {uploaded_file.name}"

    if not display_question:
        display_question = "Uploaded file"

    chat_date, chat_time = save_chat(display_question, answer)

    st.session_state.chat_history.append(
        {
            "question": display_question,
            "answer": answer,
            "date": chat_date,
            "time": chat_time,
        }
    )


                                              # COMPACT MODEL INSTRUCTIONS
SYSTEM_INSTRUCTION = (
    "You are EduSearch AI, an academic tutor. Explain uploaded documents accurately and in detail, "
    "using the document as the primary source. Cover the main ideas, definitions, processes, examples, "
    "important details, and study implications. Do not invent facts; clearly label anything not found "
    "in the document. Use clear headings, bullets, and step-by-step explanations suitable for a college student."
)
                                           # GENERATE GEMINI RESPONSE
def generate_answer(question, uploaded_file=None):
    last_error = None

    for api_key in API_KEYS:
        temp_file_path = None
        try:
            client = genai.Client(api_key=api_key)
            contents = []

            if uploaded_file is not None:
                temp_file_path = os.path.join(
                    BASE_DIR,
                    f".upload_{uuid4().hex}_{Path(uploaded_file.name).name}"
                )

                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                gemini_file = client.files.upload(file=temp_file_path)
                contents.append(gemini_file)

                if question:
                    user_prompt = (
                        f"File: {Path(uploaded_file.name).name}\n"
                        f"Answer this question using the file when relevant:\n{question}"
                    )
                else:
                    user_prompt = (
                        "Explain this uploaded document in detail for a college student. Cover its structure, "
                        "main topics, key definitions, important concepts, processes, examples, likely exam points, "
                        "and a short final recap. Base every document-specific claim on the file."
                    )
            else:
                user_prompt = question or "What are the most important study points?"

            contents.append(user_prompt)

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=contents,
                config={
                    "system_instruction": SYSTEM_INSTRUCTION,
                    "max_output_tokens": 1200,
                }
            )

            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass

            if response.text:
                return response.text

            return "⚠️ Gemini did not return an answer."

        except Exception as e:
            last_error = e
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass
            continue

    return f"""
### ❌ Error

Unable to generate an answer.

**Error:**
`{str(last_error) if last_error else 'No valid Gemini API keys were available.'}`
"""


                              # SAVE CHAT TO SQLITE
def save_chat(question, answer):

    now = datetime.now()

    chat_date = now.strftime("%d-%m-%Y")
    chat_time = now.strftime("%I:%M %p")
    current_user = st.session_state.get("auth_user") or {}
    user_id = current_user.get("id", 0)

    cursor.execute(
        """
        INSERT INTO chats
        (user_id, question, answer, date, time, deleted)
        VALUES (?, ?, ?, ?, ?, 0)
        """,
        (
            user_id,
            question,
            answer,
            chat_date,
            chat_time
        )
    )

    conn.commit()

    return chat_date, chat_time


def get_recent_chats(limit=None, search_text=""):
    current_user = st.session_state.get("auth_user") or {}
    user_id = current_user.get("id", 0)
    query = """
        SELECT id, question, answer, date, time
        FROM chats
        WHERE user_id = ? AND deleted = 0
    """
    params = [user_id]

    if search_text:
        query += " AND (question LIKE ? OR answer LIKE ?)"
        pattern = f"%{search_text}%"
        params.extend([pattern, pattern])

    query += " ORDER BY id DESC"

    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)

    cursor.execute(query, tuple(params))
    return cursor.fetchall()


def delete_recent_chat(chat_id):
    current_user = st.session_state.get("auth_user") or {}
    user_id = current_user.get("id", 0)
    cursor.execute(
        """
        UPDATE chats
        SET deleted = 1
        WHERE id = ? AND user_id = ?
        """,
        (chat_id, user_id),
    )
    conn.commit()
    if st.session_state.recent_chat_id == chat_id:
        st.session_state.recent_chat_id = None
    st.rerun()


def delete_all_recent_chats():
    current_user = st.session_state.get("auth_user") or {}
    user_id = current_user.get("id", 0)
    cursor.execute(
        """
        UPDATE chats
        SET deleted = 1
        WHERE user_id = ? AND deleted = 0
        """,
        (user_id,),
    )
    conn.commit()
    st.session_state.recent_chat_id = None
    st.rerun()


quick_prompts = [
    "Summarize this topic in simple steps",
    "Explain this like I'm a beginner",
    "Give me exam-style questions and answers",
    "Find key concepts and important facts",
]

chat_tab, recent_tab, history_tab = st.tabs(["Chat", "Recent Chats", "AI History"])

with chat_tab:
    st.markdown(
        """
        <div class="ai-tool-panel">
            <div class="panel-label">Quick prompts</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    prompt_cols = st.columns(4)
    for idx, label in enumerate(quick_prompts):
        with prompt_cols[idx]:
            if st.button(label, key=f"prompt_{idx}", use_container_width=True):
                handle_prompt(label)

                                  # DISPLAY CURRENT SESSION CHAT HISTORY
    for chat in st.session_state.chat_history:

        with st.chat_message("user"):

            st.markdown(f"<div class='prompt-bubble'>{chat['question']}</div>", unsafe_allow_html=True)

            st.caption(
                f'{chat["date"]} | {chat["time"]}'
            )


        with st.chat_message("assistant"):

            st.markdown(f"<div class='assistant-answer'>{chat['answer']}</div>", unsafe_allow_html=True)
                                # CHAT INPUT
    prompt = st.chat_input(

        "Ask me anything or upload a file...",

        accept_file=True,

        file_type=[
            "pdf",
            "txt",
            "docx",
            "csv",
            "png",
            "jpg",
            "jpeg"
        ],

        max_upload_size=200
    )
                                  # PROCESS USER INPUT
    if prompt:
        question = prompt.text.strip()
        uploaded_files = prompt.files

        uploaded_file = None
        if uploaded_files:
            uploaded_file = uploaded_files[0]

        handle_prompt(question, uploaded_file)

with recent_tab:
    st.markdown("### AI Result Grid")
    st.caption("Your newest AI summary conversations are shown first, with quick search and fast reopen access.")

    search_text = st.text_input(
        "Search results",
        placeholder="Search by question or answer...",
        key="recent_search",
        help="Filter your saved AI results by topic or keyword.",
    )

    all_recent_chats = get_recent_chats(search_text=search_text)
    recent_chats = all_recent_chats[:12]

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Saved results", len(all_recent_chats))
    with metric_col2:
        latest_label = all_recent_chats[0][3] + " • " + all_recent_chats[0][4] if all_recent_chats else "No results"
        st.metric("Newest", latest_label)
    with metric_col3:
        newest_question = all_recent_chats[0][1] if all_recent_chats else "No recent summary"
        st.metric("Latest topic", newest_question[:28] + ("..." if len(newest_question) > 28 else ""))

    if not recent_chats:
        st.info("No AI results match your search yet. Try a different keyword or start a new summary in the Chat tab.")
    else:
        grid_cols = st.columns(3)

        for index, (chat_id, question, answer, date, time) in enumerate(recent_chats):
            with grid_cols[index % 3]:
                with st.container():
                    st.markdown(
                        """
                        <div class="ai-result-card">
                            <div class="ai-result-date">{date} · {time}</div>
                            <div class="ai-result-title">{title}</div>
                            <div class="ai-result-tag">AI Summary</div>
                        </div>
                        """.format(
                            date=date,
                            time=time,
                            title=(question[:80] + "...") if len(question) > 80 else question,
                        ),
                        unsafe_allow_html=True,
                    )

                    action_col1, action_col2 = st.columns([2, 1])
                    with action_col1:
                        if st.button(
                            "Open",
                            key=f"recent_grid_open_{chat_id}",
                            use_container_width=True,
                            icon="📄",
                        ):
                            st.session_state.recent_chat_id = chat_id
                    with action_col2:
                        if st.button(
                            "Delete",
                            key=f"recent_grid_delete_{chat_id}",
                            use_container_width=True,
                            icon="🗑️",
                        ):
                            delete_recent_chat(chat_id)

                    if st.session_state.recent_chat_id == chat_id:
                        st.markdown("---")
                        st.caption(f"{date} | {time}")
                        st.markdown("**Question**")
                        st.write(question)
                        st.markdown("**AI Answer**")
                        st.markdown(answer)

with history_tab:
    st.markdown("### AI History")
    st.caption("Detailed timeline of your AI conversations with full date and time records.")

    history_search = st.text_input(
        "Search history",
        placeholder="Search by question or answer...",
        key="ai_history_search",
    )

    history_chats = get_recent_chats(search_text=history_search)

    if history_chats:
        if st.button(
            "Clear all AI history",
            key="clear_all_ai_history",
            type="secondary",
            use_container_width=False,
            icon="🧹",
        ):
            delete_all_recent_chats()

    if not history_chats:
        st.info("No AI history found yet. Start a conversation in the Chat tab to build your timeline.")
    else:
        st.markdown("---")
        for chat_id, question, answer, date, time in history_chats:
            short_title = question[:70] + "..." if len(question) > 70 else question
            with st.container(border=True):
                col_head, col_delete = st.columns([7, 1])
                with col_head:
                    st.markdown(
                        f"<div class='ai-history-item'><div class='ai-history-meta'>{date} • {time}</div><div class='ai-history-title'>{short_title}</div></div>",
                        unsafe_allow_html=True,
                    )
                with col_delete:
                    if st.button("Delete", key=f"history_delete_{chat_id}", use_container_width=True):
                        delete_recent_chat(chat_id)

                with st.expander("View conversation", expanded=False):
                    st.markdown("**Question**")
                    st.write(question)
                    st.markdown("**AI Answer**")
                    st.markdown(answer)

with st.sidebar:
    st.markdown(
        """
        <div class="brand-card">
            <div class="brand">
                <span class="material-symbols-outlined brand-icon">school</span>
                <div class="sidebar-title">EDUSEARCH AI</div>
            </div>
            <div class="sidebar-subtitle">Smart Practice. Better Results.</div>
        </div>
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
    
