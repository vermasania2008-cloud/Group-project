import streamlit as st
import sqlite3
from datetime import datetime
from google import genai
import os
from dotenv import load_dotenv


load_dotenv()


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

conn = sqlite3.connect(
    "chat_history.db",
    check_same_thread=False
)

cursor = conn.cursor()


# =========================================================
# CREATE CHAT TABLE
# =========================================================

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


# =========================================================
# SESSION STATE
# =========================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# =========================================================
# GEMINI API
# =========================================================

API_KEY = os.getenv("GEMINI_API_KEY")


if not API_KEY:

    st.error(
        "❌ Gemini API key not found."
    )

    st.info(
        "Please set the GEMINI_API_KEY environment variable "
        "before running the application."
    )

    st.stop()


client = genai.Client(
    api_key=API_KEY
)


# =========================================================
# PAGE TITLE
# =========================================================

st.title("✨ AI Assistant")

st.caption(
    "Ask anything. Get smart, detailed and accurate answers."
)


# =========================================================
# GEMINI RESPONSE FUNCTION
# =========================================================

def generate_answer(question, uploaded_file=None):

    try:

        contents = []


        # -------------------------------------------------
        # ADD UPLOADED FILE
        # -------------------------------------------------

        if uploaded_file is not None:

            file_bytes = uploaded_file.getvalue()

            uploaded_gemini_file = client.files.upload(
                file=file_bytes,
                config={
                    "mime_type": uploaded_file.type
                }
            )

            contents.append(
                uploaded_gemini_file
            )


        # -------------------------------------------------
        # ADD USER QUESTION
        # -------------------------------------------------

        if question:

            contents.append(question)

        else:

            contents.append(
                "Please analyze the uploaded file and explain its contents."
            )


        # -------------------------------------------------
        # GENERATE GEMINI RESPONSE
        # -------------------------------------------------

        response = client.models.generate_content(

            model="gemini-3.6-flash",

            contents=contents,

            config={
                "system_instruction": """
You are an academic AI assistant.

Help college students with academic
and technical questions.

Rules:

- Explain concepts clearly.
- Use simple language.
- Avoid unnecessary jargon.
- Use headings and bullet points where useful.
- Give examples when appropriate.
- For programming questions, provide correct code.
- For mathematical problems, explain steps clearly.
- For technical subjects, use accurate terminology.
- If a document or image is uploaded, carefully analyze it.
- Answer questions based on the uploaded document or image
  when relevant.
- If the answer is not present in the uploaded document,
  say so clearly.
- Keep answers suitable for college students.
- If you are uncertain, say so instead of making up information.
"""
            }
        )

        return response.text


    except Exception as e:

        return f"""
### ❌ Error

Unable to generate an answer.

`{str(e)}`
"""


# =========================================================
# SAVE CHAT TO SQLITE
# =========================================================

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


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for chat in st.session_state.chat_history:

    with st.chat_message("user"):

        st.write(
            chat["question"]
        )

        st.caption(
            f'{chat["date"]} | {chat["time"]}'
        )


    with st.chat_message("assistant"):

        st.markdown(
            chat["answer"]
        )


# =========================================================
# CHAT INPUT WITH FILE ATTACHMENT
# =========================================================

prompt = st.chat_input(

    "Ask me anything...",

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


# =========================================================
# PROCESS QUESTION / FILE
# =========================================================

if prompt:

    # -----------------------------------------------------
    # GET QUESTION
    # -----------------------------------------------------

    question = prompt.text.strip()


    # -----------------------------------------------------
    # GET UPLOADED FILES
    # -----------------------------------------------------

    uploaded_files = prompt.files


    # -----------------------------------------------------
    # GET FIRST FILE
    # -----------------------------------------------------

    uploaded_file = None

    if uploaded_files:

        uploaded_file = uploaded_files[0]


    # -----------------------------------------------------
    # DISPLAY USER MESSAGE
    # -----------------------------------------------------

    with st.chat_message("user"):

        if question:

            st.write(question)

        if uploaded_file:

            st.caption(
                f"📎 {uploaded_file.name}"
            )


    # -----------------------------------------------------
    # GENERATE AI RESPONSE
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("🤖 Thinking..."):

            answer = generate_answer(
                question,
                uploaded_file
            )

        st.markdown(answer)


    # =========================================================
    # SAVE CHAT
    # =========================================================

    display_question = question

    if not display_question and uploaded_file:
        display_question = f"📎 {uploaded_file.name}"

    if not display_question:
        display_question = "Uploaded file"


    chat_date, chat_time = save_chat(
        display_question,
        answer
    )


    # =========================================================
    # SAVE TO SESSION STATE
    # =========================================================

    st.session_state.chat_history.append(
        {
            "question": display_question,
            "answer": answer,
            "date": chat_date,
            "time": chat_time
        }
    )


# =========================================================
# REFRESH
# =========================================================

st.rerun()