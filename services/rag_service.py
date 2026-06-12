import pandas as pd

from services.chunking_service import (
    chunk_text,
    retrieve_best_chunk
)

from backend.llm_engine import call_openai


def read_uploaded_document(uploaded_file):

    if uploaded_file is None:
        return ""

    file_name = uploaded_file.name.lower()

    try:
        if file_name.endswith(".txt"):
            return uploaded_file.read().decode("utf-8", errors="ignore")

        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            return df.to_string(index=False)

        if file_name.endswith(".pdf"):
            from PyPDF2 import PdfReader

            reader = PdfReader(uploaded_file)
            text = ""

            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

            return text

        if file_name.endswith(".docx"):
            from docx import Document

            doc = Document(uploaded_file)
            return "\n".join([p.text for p in doc.paragraphs])

    except Exception as e:
        return f"Error reading document: {str(e)}"

    return ""


def build_rag_context(document_text, question, strategy, chunk_size, overlap, top_k=3):

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

    top_chunks = scored_chunks[:top_k] if scored_chunks else []

    context = "\n\n---\n\n".join(
        [item["chunk"] for item in top_chunks]
    )

    return {
        "chunks": chunks,
        "top_chunks": top_chunks,
        "context": context,
        "best_score": best_score
    }


def generate_rag_answer(question, context):

    prompt = f"""
You are an enterprise knowledge assistant.

Answer the user's question ONLY using the provided context.

If the answer is not available in the context, say:
"I could not find this information in the uploaded document."

Do not make up facts.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

    answer, usage = call_openai(
        prompt,
        return_usage=True
    )

    return answer.strip(), usage