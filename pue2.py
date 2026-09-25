import streamlit as st
from collections import Counter
import re
from pathlib import Path

# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------

st.set_page_config(
    page_title="EduSearch AI - Question Paper Analyzer",
    page_icon="📄",
    layout="wide"
)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
css_path = Path(__file__).parent / "style.css"
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
            <span class="brand-icon">🏫</span>
            <div class="sidebar-title">EDUSEARCH AI</div>
        </div>
        <div class="sidebar-subtitle">Smart Practice. Better Results.</div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigate",
        [
            "Dashboard",
            "Question Paper Analyzer",
            "AI Assistant",
            "Today's Achievement",
            "History",
        ],
    )

# ---------------------------------------------------
# QUESTION PAPER ANALYZER PAGE
# ---------------------------------------------------

if page == "Question Paper Analyzer":

    st.markdown(
        '<div class="section-heading"><span>📄</span><span>Question Paper Analyzer</span></div>',
        unsafe_allow_html=True,
    )
    st.write(
        "Upload multiple question papers and find the most important questions"
    )

    st.divider()

    # ------------------------------------------------
    # PDF UPLOAD
    # ------------------------------------------------

    st.subheader("Upload Question Papers")

    uploaded_files = st.file_uploader(
        "Drag & drop your PDF files here or click Browse Files",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} paper(s) uploaded")

        for file in uploaded_files:
            st.write(f"{file.name}")

    else:
        st.info("You can upload multiple PDF files at once.")

    # ------------------------------------------------
    # ANALYZE BUTTON
    # ------------------------------------------------

    analyze = st.button(
        "Analyze Papers",
        use_container_width=True,
        icon="🔎"
    )

    # Variables
    questions = []

    # ------------------------------------------------
    # PDF ANALYSIS
    # ------------------------------------------------

    if analyze:

        if not uploaded_files:
            st.warning("Please upload at least one PDF question paper.")

        else:

            with st.spinner("Analyzing question papers..."):

                try:
                    from pypdf import PdfReader

                    for pdf_file in uploaded_files:

                        reader = PdfReader(pdf_file)

                        full_text = ""

                        for page in reader.pages:
                            text = page.extract_text()

                            if text:
                                full_text += text + "\n"

                        # --------------------------------
                        # Extract numbered and math-style questions
                        # --------------------------------

                        question_start_pattern = re.compile(
                            r"^\s*(?:Q(?:uestion)?\s*)?(?:\d+(?:[A-Za-z])?|[IVXLC]+)(?:\s*(?:[.):-]|\([A-Za-z0-9]+\)|[A-Za-z]\)))",
                            flags=re.IGNORECASE,
                        )

                        current_question = []

                        for line in full_text.splitlines():
                            stripped = line.strip()
                            if not stripped:
                                continue

                            if question_start_pattern.match(stripped):
                                if current_question:
                                    question = " ".join(current_question)
                                    question = " ".join(question.split())
                                    if len(question) > 10:
                                        questions.append(question)
                                current_question = [stripped]
                            elif current_question:
                                current_question.append(stripped)
                            else:
                                current_question = [stripped]

                        if current_question:
                            question = " ".join(current_question)
                            question = " ".join(question.split())
                            if len(question) > 10:
                                questions.append(question)

                except ImportError:

                    st.error(
                        "pypdf is not installed. Run: pip install pypdf"
                    )

                except Exception as e:

                    st.error(f"Error while reading PDF: {e}")

            # ------------------------------------------------
            # QUESTION FREQUENCY
            # ------------------------------------------------

            if questions:

                # Normalize questions
                normalized_questions = []

                for question in questions:

                    q = question.lower()

                    # Remove unnecessary spaces
                    q = re.sub(r"\s+", " ", q)

                    normalized_questions.append(q)

                question_count = Counter(normalized_questions)

                # Sort according to frequency
                important_questions = question_count.most_common()

                # ------------------------------------------------
                # STATISTICS
                # ------------------------------------------------

                total_questions = len(questions)

                repeated_questions = sum(
                    1 for q, count in question_count.items()
                    if count > 1
                )

                important_count = sum(
                    1 for q, count in question_count.items()
                    if count >= 2
                )

                # ------------------------------------------------
                # METRICS
                # ------------------------------------------------

                st.subheader("Analysis Results")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Papers Uploaded",
                        len(uploaded_files)
                    )

                with col2:
                    st.metric(
                        "Questions Found",
                        total_questions
                    )

                with col3:
                    st.metric(
                        "Repeated Questions",
                        repeated_questions
                    )

                with col4:
                    st.metric(
                        "Important Questions",
                        important_count
                    )

                st.divider()

                # ------------------------------------------------
                # IMPORTANT QUESTIONS + SUMMARY
                # ------------------------------------------------

                left, right = st.columns([3, 1])

                # --------------------------------------------
                # MOST IMPORTANT QUESTIONS
                # --------------------------------------------

                with left:

                    st.subheader("Most Important Questions")

                    st.caption(
                        "Questions are ranked by frequency across all uploaded papers"
                    )

                    if important_questions:

                        for index, (question, count) in enumerate(
                            important_questions[:10],
                            start=1
                        ):

                            col_a, col_b, col_c = st.columns(
                                [0.5, 6, 2]
                            )

                            with col_a:
                                st.write(f"**{index}**")

                            with col_b:
                                st.write(question.capitalize())

                            with col_c:

                                if count >= 3:
                                    st.error(
                                        f"Very Important • Asked {count} times"
                                    )

                                elif count == 2:
                                    st.warning(
                                        f"Important • Asked {count} times"
                                    )

                                else:
                                    st.info(
                                        f"Asked {count} time"
                                    )

                    else:
                        st.info("No questions found.")

                # --------------------------------------------
                # ANALYSIS SUMMARY
                # --------------------------------------------

                with right:

                    st.subheader("Analysis Summary")

                    st.write(
                        f"**Papers Analyzed:** {len(uploaded_files)}"
                    )

                    st.write(
                        f"**Total Questions:** {total_questions}"
                    )

                    st.write(
                        f"**Repeated Questions:** {repeated_questions}"
                    )

                    st.write(
                        f"**Important Questions:** {important_count}"
                    )

                    st.write(
                        "**Subjects Detected:** Not available"
                    )

                    st.divider()

                    st.subheader("Tips")

                    st.info(
                        """
                        Upload at least 3–5 previous year
                        question papers to get more accurate
                        and useful results.
                        """
                    )

                # ------------------------------------------------
                # VIEW ALL QUESTIONS
                # ------------------------------------------------

                st.divider()

                with st.expander("View All Questions"):

                    for i, question in enumerate(questions, 1):
                        st.write(f"**{i}.** {question}")

            else:

                st.warning(
                    "No questions could be extracted from the uploaded PDFs."
                )

# ---------------------------------------------------
# OTHER PAGES
# ---------------------------------------------------

elif page == "Dashboard":

    st.markdown(
        '<div class="section-heading"><span>📊</span><span>Dashboard</span></div>',
        unsafe_allow_html=True,
    )

    st.write("Welcome to EduSearch AI!")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Papers", 0)

    with col2:
        st.metric("Questions", 0)

    with col3:
        st.metric("Important Questions", 0)


elif page == "AI Assistant":

    st.markdown(
        '<div class="section-heading"><span>🤖</span><span>AI Assistant</span></div>',
        unsafe_allow_html=True,
    )

    st.write("Ask questions about your academic papers.")

    question = st.text_input(
        "Enter your question"
    )

    if st.button("Ask AI"):

        if question:
            st.info(
                "AI Assistant functionality can be connected here."
            )
        else:
            st.warning("Please enter a question.")


elif page == "Today's Achievement":

    st.markdown(
        '<div class="section-heading"><span>🏆</span><span>Today\'s Achievement</span></div>',
        unsafe_allow_html=True,
    )

    st.success("Keep studying and achieve your goals!")


elif page == "History":

    st.markdown(
        '<div class="section-heading"><span>🕘</span><span>History</span></div>',
        unsafe_allow_html=True,
    )

    st.info("Your previous analysis history will appear here.")


