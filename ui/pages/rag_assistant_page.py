import streamlit as st
import pandas as pd

from services.rag_service import (
    read_uploaded_document,
    build_rag_context,
    generate_rag_answer
)

from services.token_usage_service import save_token_usage


def render_rag_assistant():

    st.subheader("🤖 Enterprise RAG Knowledge Assistant")

    st.info(
        "Upload a document, ask a question, and get an answer grounded only in the uploaded content."
    )

    uploaded_file = st.file_uploader(
        "Upload knowledge document",
        type=["txt", "csv", "pdf", "docx"],
        key="rag_doc_upload"
    )

    default_text = ""

    if uploaded_file:
        default_text = read_uploaded_document(uploaded_file)

        if default_text:
            st.success(f"Loaded document: {uploaded_file.name}")
        else:
            st.warning("Unable to read uploaded document.")

    document_text = st.text_area(
        "Document content",
        value=default_text,
        height=280,
        key="rag_document_text"
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        question = st.text_area(
            "Ask a question about this document",
            value="What are the key reimbursement rules?",
            height=90,
            key="rag_question"
        )

    with col2:
        strategy = st.selectbox(
            "Chunking strategy",
            [
                "Fixed-size chunking",
                "Overlap chunking",
                "Paragraph chunking",
                "Sentence chunking",
                "Semantic chunking"
            ],
            index=1,
            key="rag_strategy"
        )

        chunk_size = st.slider(
            "Chunk size",
            min_value=100,
            max_value=1000,
            value=350,
            step=50,
            key="rag_chunk_size"
        )

        overlap = st.slider(
            "Overlap",
            min_value=0,
            max_value=300,
            value=80,
            step=20,
            key="rag_overlap"
        )

        top_k = st.slider(
            "Top chunks",
            min_value=1,
            max_value=5,
            value=3,
            step=1,
            key="rag_top_k"
        )

    if st.button("Ask RAG Assistant", use_container_width=True):

        if not document_text.strip():
            st.error("Please upload or paste document content.")
            st.stop()

        if not question.strip():
            st.error("Please enter a question.")
            st.stop()

        with st.spinner("Retrieving relevant chunks..."):

            rag_result = build_rag_context(
                document_text=document_text,
                question=question,
                strategy=strategy,
                chunk_size=chunk_size,
                overlap=overlap,
                top_k=top_k
            )

        with st.spinner("Generating grounded answer..."):

            answer, usage = generate_rag_answer(
                question,
                rag_result["context"]
            )

        save_token_usage(
            st.session_state.user["id"],
            st.session_state.user["email"],
            "Enterprise RAG Assistant",
            usage
        )

        st.markdown("### 🤖 Answer")
        st.success(answer)

        st.markdown("### 📌 Retrieved Source Chunks")

        for item in rag_result["top_chunks"]:
            with st.expander(
                f"Chunk {item['chunk_number']} | Score: {item['score']}"
            ):
                st.write(item["chunk"])

        st.markdown("### 📊 Retrieval Summary")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Total Chunks", len(rag_result["chunks"]))

        with c2:
            st.metric("Top Chunks Used", len(rag_result["top_chunks"]))

        with c3:
            st.metric("Best Match Score", rag_result["best_score"])

        score_df = pd.DataFrame(rag_result["top_chunks"])

        if not score_df.empty:
            score_df = score_df[["chunk_number", "score", "chunk"]]
            score_df = score_df.rename(
                columns={
                    "chunk_number": "Chunk No",
                    "score": "Match Score",
                    "chunk": "Retrieved Text"
                }
            )

            st.dataframe(
                score_df,
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No retrieved chunks found.")