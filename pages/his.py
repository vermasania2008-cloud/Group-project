import streamlit as st
import sqlite3
from pathlib import Path

from auth import auth_gate, render_logout_button, render_page_link


# =========================================================
# DATABASE PATH
# =========================================================

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "chat_history.db"


# =========================================================
# PAGE TITLE
# =========================================================

auth_gate()

st.markdown(
    '<div class="section-heading"><span class="material-symbols-outlined">history</span><span>Chat History</span></div>',
    unsafe_allow_html=True,
)

st.caption(
    "View and manage your previous conversations with the AI Assistant."
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

conn = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)

cursor = conn.cursor()

#============================================
#sidebar 
#============================================

css_path = Path(__file__).parent / "his.css" 
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
            <span class="material-symbols-outlined brand-icon"></span>
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




# =========================================================
# CREATE TABLE IF NOT EXISTS
# =========================================================

user_id = st.session_state.get("auth_user", {}).get("id", 0)

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
if "open_chat" not in st.session_state:
    st.session_state.open_chat = None

if "confirm_delete_all" not in st.session_state:
    st.session_state.confirm_delete_all = False

if "confirm_empty_trash" not in st.session_state:
    st.session_state.confirm_empty_trash = False

                                           # TABS
history_tab, deleted_tab = st.tabs(
    [
        "Chat History",
        "Deleted History"
    ]
)

                                            # CHAT HISTORY TAB
with history_tab:

    st.markdown("### Your Conversations")

                                             # SEARCH
    search = st.text_input(
        "Search your conversations",
        placeholder="Search by question...",
        key="history_search",
        icon="🔎"
    )

                                              # GET ACTIVE CONVERSATIONS
    if search:

        cursor.execute(
            """
            SELECT id, question, answer, date, time
            FROM chats
            WHERE user_id = ?
            AND deleted = 0
            AND question LIKE ?
            ORDER BY id DESC
            """,
            (user_id, f"%{search}%")
        )

    else:

        cursor.execute(
            """
            SELECT id, question, answer, date, time
            FROM chats
            WHERE user_id = ?
            AND deleted = 0
            ORDER BY id DESC
            """,
            (user_id,)
        )


    chats = cursor.fetchall()

                                               # CONVERSATION COUNT
    if chats:

        st.success(
            f"{len(chats)} conversation(s) found."
        )

    else:

        st.info(
            "No conversations found."
        )

                                                # DISPLAY ACTIVE CONVERSATIONS
    for chat in chats:

        chat_id = chat[0]
        question = chat[1]
        answer = chat[2]
        date = chat[3]
        time = chat[4]

                                                # SHORT TITLE
        if len(question) > 70:

            title = question[:70] + "..."

        else:

            title = question

                                                 # CHAT HEADER
        col1, col2 = st.columns([6, 1])

                                                 # OPEN / CLOSE CHAT
        with col1:

            if st.button(
                f"{title}",
                key=f"open_{chat_id}",
                use_container_width=True,
                icon="💬"
            ):

                if st.session_state.open_chat == chat_id:

                    st.session_state.open_chat = None

                else:

                    st.session_state.open_chat = chat_id

                                                 # MOVE TO DELETED HISTORY
        with col2:

            if st.button(
                "",
                key=f"delete_{chat_id}",
                help="Move this conversation to Deleted History",
                icon="🗑️"
            ):

                cursor.execute(
                    """
                    UPDATE chats
                    SET deleted = 1
                    WHERE id = ? AND user_id = ?
                    """,
                    (chat_id, user_id)
                )

                conn.commit()


                # Close chat if it was open

                if st.session_state.open_chat == chat_id:

                    st.session_state.open_chat = None


                st.rerun()

                                                # SHOW CONVERSATION
        if st.session_state.open_chat == chat_id:

            with st.container(border=True):

                st.caption(
                    f"{date}   |   {time}"
                )

                st.markdown(
                    "### Your Question"
                )

                st.write(question)

                st.markdown(
                    "### 🤖 AI Answer"
                )

                st.markdown(answer)

                                                # DELETE ALL ACTIVE HISTORY
    if chats:

        st.markdown("---")

        st.markdown(
            "### Delete History"
        )

        if st.button(
            "Move All History to Deleted",
            type="secondary",
            icon="🗑️"
        ):

            st.session_state.confirm_delete_all = True

                                                  # CONFIRM DELETE ALL
        if st.session_state.confirm_delete_all:

            st.warning(
                "Are you sure you want to move ALL conversations "
                "to Deleted History?"
            )

            col1, col2 = st.columns(2)


            with col1:

                if st.button(
                    "Yes, Move All",
                    use_container_width=True,
                    icon="✅",
                ):

                    cursor.execute(
                        """
                        UPDATE chats
                        SET deleted = 1
                        WHERE user_id = ? AND deleted = 0
                        """,
                        (user_id,)
                    )

                    conn.commit()

                    st.session_state.open_chat = None
                    st.session_state.confirm_delete_all = False

                    st.rerun()


            with col2:

                if st.button(
                    "Cancel",
                    use_container_width=True,
                    icon="❌"
                ):

                    st.session_state.confirm_delete_all = False

                    st.rerun()

                                                    # DELETED HISTORY TAB
with deleted_tab:

    st.markdown("### Deleted History")

    st.caption(
        "Deleted conversations are kept here until you permanently remove them."
    )

                                                    # GET DELETED CONVERSATIONS
    cursor.execute(
        """
        SELECT id, question, answer, date, time
        FROM chats
        WHERE user_id = ? AND deleted = 1
        ORDER BY id DESC
        """,
        (user_id,)
    )

    deleted_chats = cursor.fetchall()

                                                      # DELETED COUNT
    if deleted_chats:

        st.warning(
            f"{len(deleted_chats)} deleted conversation(s)."
        )

    else:

        st.info(
            "No deleted conversations."
        )

                                                      # DISPLAY DELETED CONVERSATIONS
    for chat in deleted_chats:

        chat_id = chat[0]
        question = chat[1]
        answer = chat[2]
        date = chat[3]
        time = chat[4]

                                                      # SHORT TITLE
        if len(question) > 70:

            title = question[:70] + "..."

        else:

            title = question

                    # DELETED CHAT HEADER
        col1, col2, col3 = st.columns([5, 1, 1])

                    # OPEN DELETED CHAT
        with col1:

            if st.button(
                f"{title}",
                key=f"deleted_open_{chat_id}",
                use_container_width=True,
                icon="💬"
            ):

                if st.session_state.open_chat == chat_id:

                    st.session_state.open_chat = None

                else:

                    st.session_state.open_chat = chat_id

                    # RESTORE CHAT
                    with col2:

                     if st.button(
                "",
                key=f"restore_{chat_id}",
                help="Restore this conversation",
                icon="↩️",
            ):

                        cursor.execute(
                    """
                    UPDATE chats
                    SET deleted = 0
                    WHERE id = ? AND user_id = ?
                    """,
                    (chat_id, user_id)
                )

                conn.commit()

                st.session_state.open_chat = None

                st.rerun()

                    # PERMANENT DELETE
        with col3:

            if st.button(
                "",
                key=f"permanent_{chat_id}",
                help="Delete permanently",
                icon="🗑️"
            ):

                cursor.execute(
                    """
                    DELETE FROM chats
                    WHERE id = ? AND user_id = ?
                    """,
                    (chat_id, user_id)
                )

                conn.commit()

                st.session_state.open_chat = None

                st.rerun()

                    # SHOW DELETED 
        if st.session_state.open_chat == chat_id:
          with st.container(border=True):
                st.caption(
                    f"{date}   |   {time}"
                )
                st.markdown(
                    "### Your Question"
                )
                st.write(question)
                st.markdown(
                    "### 🤖 AI Answer"
                )
                st.markdown(answer)
    # EMPTY TRASH
    if deleted_chats:
        st.markdown("---")
        st.markdown(
            "### Empty Deleted History"
        )
        if st.button(
            "Permanently Delete All Deleted Conversations",
            type="secondary",
            icon="🧹"
        ):
            st.session_state.confirm_empty_trash = True
                                                
                                                    # CONFIRM EMPTY TRASH
        if st.session_state.confirm_empty_trash:
            st.error(
                "This will permanently delete all conversations "
                "from Deleted History. This action cannot be undone."
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    "Yes, Delete Permanently",
                    use_container_width=True,
                    icon="✅"
                ):
                    cursor.execute(
                        """
                        DELETE FROM chats
                        WHERE user_id = ? AND deleted = 1
                        """,
                        (user_id,)
                    )
                    conn.commit()
                    st.session_state.open_chat = None
                    st.session_state.confirm_empty_trash = False
                    st.rerun()
            with col2:
                if st.button(
                    "Cancel",
                    use_container_width=True,
                    icon="❌"
                ):
                    st.session_state.confirm_empty_trash = False
                    st.rerun()
                                               # CLOSE DATABASE
conn.close()