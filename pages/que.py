from io import BytesIO
from pathlib import Path
import re

import pandas as pd
import streamlit as st
from pypdf import PdfReader

st.set_page_config(
    page_title="ExamPrep AI",
    page_icon=":material/school:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,400,0,0" />',
    unsafe_allow_html=True,
)

css_path = Path(__file__).resolve().parent.parent / "style.css"
if css_path.exists():
    st.markdown(
        f"<style>{css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )
else:
    st.error(f"CSS file not found: {css_path}")


def extract_questions(text):
    """Split extracted paper text into manageable question blocks for math papers."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    question_start_pattern = re.compile(
        r"^\s*(?:Q(?:uestion)?\s*)?(?:\d+(?:[A-Za-z])?|[IVXLC]+)(?:\s*(?:[.):-]|\([A-Za-z0-9]+\)|[A-Za-z]\)))",
        flags=re.IGNORECASE,
    )

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    questions = []
    current_question = []

    for line in lines:
        if question_start_pattern.match(line):
            if current_question:
                question_text = " ".join(current_question)
                if question_text.strip():
                    questions.append(re.sub(r"\s+", " ", question_text).strip())
            current_question = [line]
        elif current_question:
            current_question.append(line)
        else:
            current_question = [line]

    if current_question:
        question_text = " ".join(current_question)
        if question_text.strip():
            questions.append(re.sub(r"\s+", " ", question_text).strip())

    if not questions:
        return [re.sub(r"\s+", " ", line).strip() for line in lines if line.strip()]

    return questions


def extract_pdf_text(uploaded_file):
    """Extract embedded text while preserving useful errors for the UI."""
    pdf_reader = PdfReader(BytesIO(uploaded_file.getvalue()))

    if pdf_reader.is_encrypted:
        try:
            if not pdf_reader.decrypt(""):
                raise ValueError("This PDF is password-protected.")
        except Exception as error:
            raise ValueError("This PDF is password-protected.") from error

    page_text = []
    for page in pdf_reader.pages:
        text = page.extract_text() or ""
        if not text.strip():
            text = page.extract_text(extraction_mode="layout") or ""
        page_text.append(text)

    extracted_text = "\n".join(page_text).strip()
    if not extracted_text:
        raise ValueError(
            "This PDF contains no selectable text. It may be a scanned document "
            "and needs OCR before analysis."
        )
    return extracted_text


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

    st.page_link("dash.py", label="Dashboard", icon=":material/dashboard:")
    st.page_link("pages/que.py", label="Question Paper Analyzer", icon=":material/document_scanner:")
    st.page_link("pages/ai.py", label="AI Assistant", icon=":material/psychology:")
    st.page_link("pages/tda.py", label="Today Achievement", icon=":material/workspace_premium:")
    st.page_link("pages/his.py", label="History", icon=":material/history:")
    

st.markdown(
    """
    <div class="hero-panel analyzer-hero">
        <div class="hero-copy">
            <div class="hero-kicker"><span class="material-symbols-outlined">document_scanner</span> SMART PAPER ANALYSIS</div>
            <h1>Question paper analyser</h1>
            <p>Upload previous papers and surface the questions worth your attention.</p>
            <div class="hero-status"><span class="status-dot"></span> PDF intelligence online</div>
        </div>
        <div class="hero-art" aria-hidden="true">
            <span class="material-symbols-outlined hero-art-main">picture_as_pdf</span>
            <span class="material-symbols-outlined hero-art-small hero-art-one">search</span>
            <span class="material-symbols-outlined hero-art-small hero-art-two">task_alt</span>
            <span class="hero-orbit"></span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-heading"><span class="material-symbols-outlined">upload_file</span><span>Upload your question papers</span></div>',
    unsafe_allow_html=True,
)
uploaded_files = st.file_uploader(
    "Upload multiple PDF question papers",
    type=["pdf"],
    accept_multiple_files=True,
)
st.markdown(
    '<div class="upload-note"><span class="material-symbols-outlined">verified</span><span>PDF text is extracted locally for fast, private analysis.</span></div>',
    unsafe_allow_html=True,
)
extracted_papers = []

if uploaded_files:
    unreadable_files = []
    scanned_files = []
    for uploaded_file in uploaded_files:
        try:
            extracted_text = extract_pdf_text(uploaded_file)
        except ValueError as error:
            if "no selectable text" in str(error):
                scanned_files.append(uploaded_file.name)
            else:
                unreadable_files.append(f"{uploaded_file.name} ({error})")
            continue
        except Exception as error:
            unreadable_files.append(f"{uploaded_file.name} ({error})")
            continue

        extracted_papers.append((uploaded_file.name, extracted_text))

    st.caption(f"Loaded {len(uploaded_files)} paper(s)")
    if unreadable_files:
        st.warning(
            "Could not read: " + ", ".join(unreadable_files) + "."
        )
    if scanned_files:
        st.warning(
            "No selectable text found in: "
            + ", ".join(scanned_files)
            + ". These scanned PDFs need OCR before analysis."
        )

if st.button("Analyze paper", type="primary"):
    if not uploaded_files:
        st.warning("Upload at least one PDF before analyzing.")
    else:
        all_question_rows = []
        for paper_name, extracted_text in extracted_papers:
            for question in extract_questions(extracted_text):
                normalized_question = re.sub(r"\s+", " ", question).strip().lower()
                all_question_rows.append(
                    {
                        "Question": question,
                        "Paper": paper_name,
                        "Normalized Question": normalized_question,
                    }
                )

        if not all_question_rows:
            st.warning("No selectable text was found in the uploaded PDFs.")
            st.stop()

        repeated_counts = {}
        for row in all_question_rows:
            repeated_counts[row["Normalized Question"]] = repeated_counts.get(row["Normalized Question"], 0) + 1

        analysis_rows = []
        repeated_question_groups = {}

        for row in all_question_rows:
            normalized_question = row["Normalized Question"]
            occurrence_count = repeated_counts[normalized_question]
            is_repeated = occurrence_count > 1

            entry = {
                "Question": row["Question"],
                "Paper": row["Paper"],
                "Occurrences": occurrence_count,
                "Repeated Question": "Yes" if is_repeated else "No",
            }
            analysis_rows.append(entry)

            if is_repeated:
                if normalized_question not in repeated_question_groups:
                    repeated_question_groups[normalized_question] = {
                        "Question": row["Question"],
                        "Occurrences": occurrence_count,
                        "Papers": {row["Paper"]},
                    }
                else:
                    repeated_question_groups[normalized_question]["Occurrences"] = occurrence_count
                    repeated_question_groups[normalized_question]["Papers"].add(row["Paper"])

        analysis = pd.DataFrame(
            [
                {"Question": row["Question"], "Paper": row["Paper"], "Occurrences": row["Occurrences"], "Repeated Question": row["Repeated Question"]}
                for row in analysis_rows
            ]
        )

        repeated_questions_df = pd.DataFrame(
            [
                {
                    "Question": details["Question"],
                    "Occurrences": details["Occurrences"],
                    "Papers": ", ".join(sorted(details["Papers"])),
                }
                for details in repeated_question_groups.values()
            ],
            columns=["Question", "Occurrences", "Papers"],
        )

        if not repeated_questions_df.empty:
            repeated_questions_df = repeated_questions_df.sort_values(
                ["Occurrences", "Question"], ascending=[False, True]
            )

        st.session_state["papers_analyzed"] = len(uploaded_files)
        st.session_state["questions_analyzed"] = len(analysis)
        st.session_state["topics_detected"] = 0

        total, papers = st.columns(2)
        total.metric("Total questions", len(analysis))
        papers.metric("Papers processed", len(uploaded_files))

        st.markdown(
            '<div class="section-heading"><span>📊</span><span>Paper breakdown</span></div>',
            unsafe_allow_html=True,
        )

        left_col, right_col = st.columns([2.2, 1.2])
        with left_col:
            st.dataframe(analysis, width="stretch", hide_index=True)

        with right_col:
            st.markdown(
                '<div class="card-heading"><span>🔁</span><span>Repeated questions</span></div>',
                unsafe_allow_html=True,
            )
            if repeated_questions_df.empty:
                st.info("No repeated questions were found in the uploaded PDFs.")
            else:
                st.metric("Repeated question sets", len(repeated_questions_df))
                st.metric("Repeat occurrences", int(repeated_questions_df["Occurrences"].sum()))
                st.dataframe(
                    repeated_questions_df,
                    width="stretch",
                    hide_index=True,
                    use_container_width=True,
                )

        st.download_button(
            "Download analysis CSV",
            analysis.to_csv(index=False).encode("utf-8"),
            "question-paper-analysis.csv",
        )
