
import streamlit as st    
import sqlite3
from datetime import datetime
from google import genai
import os
from pathlib import Path

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
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))

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
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL
)
""")

conn.commit()

                                  # SESSION STATE
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
                                
                                  # GEMINI API
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.markdown(
        """
        <div class="notice-box error-box">
            <span class="material-symbols-outlined">error</span>
            <div>
                <strong>Gemini API key not found.</strong>
                <small>Please add GEMINI_API_KEY to your .env file.</small>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


client = genai.Client(
    api_key=API_KEY
)

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


                                   # GEMINI SYSTEM INSTRUCTION
SYSTEM_INSTRUCTION = """
You are an academic AI assistant for college students.

Your job is to answer the student's question clearly,
accurately and in simple language.

IMPORTANT RULES FOR UPLOADED FILES:

1. If a file is uploaded, carefully inspect and understand
   the entire relevant content of the file before answering.

2. Treat the uploaded file as an important source of context.

3. If the student's question asks about the uploaded file,
   answer using information from that file.

4. Do not ignore the uploaded file.

5. If the answer can be found in the uploaded file,
   explain the answer based on the file.

6. If the question asks you to summarize, explain, analyze,
   extract questions, find topics, identify important points,
   or answer a question from the uploaded file, perform that
   task using the uploaded file.

7. If the answer is NOT available in the uploaded file,
   clearly say that the information was not found in the
   uploaded file. You may then provide general knowledge
   separately if it is useful.

8. Never pretend that information came from the uploaded file
   when it did not.

GENERAL RULES:

- Explain concepts clearly.
- Use simple language suitable for college students.
- Use headings and bullet points when useful.
- Give examples when appropriate.
- For programming questions, provide correct code.
- For mathematical problems, explain the steps.
- For technical subjects, use accurate terminology.
- If you are uncertain, say so instead of making up information.
- Do not give unnecessarily complicated answers.
"""
                                           # GENERATE GEMINI RESPONSE
def generate_answer(question, uploaded_file=None):

    try:

        contents = []
                                           # FILE HANDLING
        if uploaded_file is not None:

                                           # Save uploaded file temporarily
            temp_file_path = os.path.join(
                BASE_DIR,
                f"temp_{uploaded_file.name}"
            )

            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getvalue())


            # Upload file to Gemini
            gemini_file = client.files.upload(
                file=temp_file_path
            )


            # Add file to Gemini request
            contents.append(gemini_file)
                                       
                              # BUILD USER PROMPT
            if question:

               if uploaded_file:

                user_prompt = f"""
The student has uploaded a file named:

{uploaded_file.name}

Carefully inspect the uploaded file first.

Then answer the student's question based on the
uploaded file whenever the question is related to it.

Student's question:

{question}

Make it clear which information comes from the
uploaded file when appropriate.
"""

            else:

                user_prompt = question

        else:

            user_prompt = """
Please carefully analyze the uploaded file.

Provide a useful explanation of its contents.

Identify the main topics, important concepts,
and important information that a college student
should understand.
"""


        contents.append(user_prompt)
                            # GENERATE RESPONSE
        response = client.models.generate_content(

            model="gemini-3.6-flash",

            contents=contents,

            config={
                "system_instruction": SYSTEM_INSTRUCTION
            }
        )
                            # DELETE TEMPORARY FILE
        try:

            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

        except Exception:
            pass
                             # RETURN ANSWER
        if response.text:

            return response.text

        return "⚠️ Gemini did not return an answer."


    except Exception as e:

        return f"""
### ❌ Error

Unable to generate an answer.

**Error:**
`{str(e)}`
"""
                              # SAVE CHAT TO SQLITE
def save_chat(question, answer):

    now = datetime.now()

    chat_date = now.strftime("%d-%m-%Y")
    chat_time = now.strftime("%I:%M %p")


    cursor.execute(
        """
        INSERT INTO chats
        (question, answer, date, time)
        VALUES (?, ?, ?, ?)
        """,
        (
            question,
            answer,
            chat_date,
            chat_time
        )
    )

    conn.commit()

    return chat_date, chat_time

quick_prompts = [
    "Summarize this topic in simple steps",
    "Explain this like I'm a beginner",
    "Give me exam-style questions and answers",
    "Find key concepts and important facts",
]

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

    st.page_link("dash.py", label="Dashboard", icon=":material/dashboard:")
    st.page_link("pages/que.py", label="Question Paper Analyzer", icon=":material/document_scanner:")
    st.page_link("pages/ai.py", label="AI Assistant", icon=":material/psychology:")
    st.page_link("pages/tda.py", label="Today Achievement", icon=":material/workspace_premium:")
    st.page_link("pages/his.py", label="History", icon=":material/history:")
    
