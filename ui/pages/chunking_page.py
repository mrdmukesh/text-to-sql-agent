import pandas as pd
import streamlit as st

from services.chunking_service import (
    chunk_text,
    retrieve_best_chunk,
    generate_demo_answer,
    explain_strategy
)


def read_uploaded_document(uploaded_file):

    if uploaded_file is None:
        return ""

    file_name = uploaded_file.name.lower()

    try:

        # TXT
        if file_name.endswith(".txt"):
            return uploaded_file.read().decode(
                "utf-8",
                errors="ignore"
            )

        # CSV
        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            return df.to_string(index=False)

        # PDF
        if file_name.endswith(".pdf"):

            from PyPDF2 import PdfReader

            reader = PdfReader(uploaded_file)

            text = ""

            for page in reader.pages:
                extracted = page.extract_text()

                if extracted:
                    text += extracted + "\n"

            return text

        # DOCX
        if file_name.endswith(".docx"):

            from docx import Document

            doc = Document(uploaded_file)

            text = "\n".join(
                [p.text for p in doc.paragraphs]
            )

            return text

    except Exception as e:
        return f"Error reading document: {str(e)}"

    return ""

def render_chunking_lab():

    st.subheader("🧩 RAG Chunking Strategy Lab")

    st.info(
        "Upload or paste a document, ask a question, select a chunking strategy, "
        "and see how retrieval changes based on chunking."
    )

    sample_text = """Company Travel and Reimbursement Policy

Employees can claim hotel expenses up to $200 per night when the travel is approved for business purposes.

Visa processing fees are reimbursable only when the travel is business-related and approved by the manager.

Food expenses are reimbursable up to $50 per day during official business travel.

Personal vacation expenses, family travel, entertainment, and non-business upgrades are not reimbursable.

All reimbursement claims must include a valid receipt or invoice and should be submitted within 30 days of the expense date."""

    uploaded_doc = st.file_uploader(
        "Upload document for chunking",
        type=["txt", "csv", "pdf", "docx"],
        key="chunking_doc_upload"
    )

    uploaded_text = ""

    if uploaded_doc:
        uploaded_text = read_uploaded_document(uploaded_doc)

        if uploaded_text:
            st.success(f"Uploaded document loaded: {uploaded_doc.name}")
        else:
            st.warning("Unable to read this file. Please upload .txt or .csv.")

    default_text = uploaded_text if uploaded_text else sample_text

    col1, col2 = st.columns([2, 1])

    with col1:
        document_text = st.text_area(
            "Paste or edit document text",
            value=default_text,
            height=330,
            key="chunking_document_text"
        )

    with col2:
        question = st.text_area(
            "User question",
            value="Can I claim visa processing fees?",
            height=90,
            key="chunking_question_area"
        )

        strategy = st.selectbox(
            "Chunking strategy",
            [
                "Fixed-size chunking",
                "Overlap chunking",
                "Paragraph chunking",
                "Sentence chunking",
                "Semantic chunking"
            ],
            key="chunking_strategy"
        )

        chunk_size = st.slider(
            "Chunk size",
            min_value=80,
            max_value=800,
            value=220,
            step=20,
            key="chunk_size_slider"
        )

        overlap = st.slider(
            "Overlap",
            min_value=0,
            max_value=300,
            value=60,
            step=20,
            key="overlap_slider"
        )

    st.markdown("---")

    if st.button("Simulate Retrieval", use_container_width=True):

        if not document_text.strip():
            st.error("Please paste text or upload a document.")
            st.stop()

        if not question.strip():
            st.error("Please enter a question.")
            st.stop()

        chunks = chunk_text(
            document_text,
            strategy,
            chunk_size,
            overlap
        )

        best_chunk, best_score, scored_chunks = retrieve_best_chunk(
            question,
            chunks
        )

        answer = generate_demo_answer(
            question,
            best_chunk
        )

        st.markdown("### Strategy Explanation")
        st.success(explain_strategy(strategy))

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Document Characters", len(document_text))

        with m2:
            st.metric("Total Chunks", len(chunks))

        with m3:
            avg_size = (
                int(sum(len(c) for c in chunks) / len(chunks))
                if chunks
                else 0
            )
            st.metric("Average Chunk Size", avg_size)

        with m4:
            st.metric("Best Match Score", best_score)

        st.markdown("---")

        tab_chunks, tab_retrieval, tab_answer, tab_compare = st.tabs(
            [
                "📦 Generated Chunks",
                "🎯 Retrieved Chunk",
                "🤖 Demo Answer",
                "📊 Score Table"
            ]
        )

        with tab_chunks:
            st.markdown("### Generated Chunks")

            for i, chunk in enumerate(chunks, start=1):
                with st.expander(f"Chunk {i} | {len(chunk)} characters"):
                    st.write(chunk)

        with tab_retrieval:
            st.markdown("### Best Retrieved Chunk")

            if best_chunk:
                st.code(best_chunk, language="text")
                st.caption(
                    "This is the chunk your RAG system would send to the LLM as context."
                )
            else:
                st.warning("No chunk retrieved.")

        with tab_answer:
            st.markdown("### Final Answer Simulation")
            st.write(answer)

            st.warning(
                "This answer is based only on the retrieved chunk. "
                "If the chunk is incomplete, the answer may also be incomplete."
            )

        with tab_compare:
            st.markdown("### Chunk Retrieval Scores")

            score_df = pd.DataFrame(scored_chunks)

            if not score_df.empty:
                score_df = score_df[
                    ["chunk_number", "score", "chunk"]
                ]

                st.dataframe(score_df)
            else:
                st.info("No scores available.")