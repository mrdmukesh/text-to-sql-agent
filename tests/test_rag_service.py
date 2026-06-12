from unittest.mock import patch, MagicMock

from services.rag_service import (
    build_rag_context,
    generate_rag_answer
)


SAMPLE_TEXT = """
Company Travel Policy

Employees can claim hotel expenses up to $200 per night.

Visa processing fees are reimbursable only when travel is business-related and approved by the manager.

Food expenses are reimbursable up to $50 per day.

Personal vacation expenses are not reimbursable.
"""


def test_build_rag_context():

    result = build_rag_context(
        document_text=SAMPLE_TEXT,
        question="Can I claim visa processing fees?",
        strategy="Overlap chunking",
        chunk_size=200,
        overlap=50,
        top_k=2
    )

    assert "chunks" in result
    assert "top_chunks" in result
    assert "context" in result

    assert len(result["chunks"]) > 0
    assert len(result["top_chunks"]) > 0

    assert "Visa processing fees" in result["context"]


@patch("services.rag_service.call_openai")
def test_generate_rag_answer(mock_call_openai):

    mock_call_openai.return_value = (
        "Yes, visa processing fees are reimbursable for business travel.",
        {
            "prompt_tokens": 100,
            "completion_tokens": 20,
            "total_tokens": 120,
            "estimated_cost": 0.001
        }
    )

    answer, usage = generate_rag_answer(
        question="Can I claim visa fees?",
        context="Visa processing fees are reimbursable."
    )

    assert "reimbursable" in answer.lower()

    assert usage["total_tokens"] == 120
    assert usage["estimated_cost"] == 0.001


def test_rag_context_retrieval_quality():

    result = build_rag_context(
        document_text=SAMPLE_TEXT,
        question="hotel expenses",
        strategy="Sentence chunking",
        chunk_size=200,
        overlap=50,
        top_k=1
    )

    top_chunk = result["top_chunks"][0]["chunk"]

    assert "hotel expenses" in top_chunk.lower()


def test_rag_empty_question():

    result = build_rag_context(
        document_text=SAMPLE_TEXT,
        question="",
        strategy="Fixed-size chunking",
        chunk_size=200,
        overlap=50,
        top_k=1
    )

    assert len(result["chunks"]) > 0


def test_rag_semantic_chunking():

    result = build_rag_context(
        document_text=SAMPLE_TEXT,
        question="food reimbursement",
        strategy="Semantic chunking",
        chunk_size=200,
        overlap=50,
        top_k=2
    )

    assert len(result["top_chunks"]) > 0