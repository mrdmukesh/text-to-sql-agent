from services.chunking_service import (
    fixed_size_chunking,
    overlap_chunking,
    paragraph_chunking,
    sentence_chunking,
    chunk_text,
    retrieve_best_chunk,
    generate_demo_answer,
    explain_strategy
)


SAMPLE_TEXT = """
Company Travel Policy

Employees can claim hotel expenses up to $200 per night.

Visa processing fees are reimbursable only when travel is business-related and approved by the manager.

Food expenses are reimbursable up to $50 per day.
"""


def test_fixed_size_chunking():

    chunks = fixed_size_chunking(SAMPLE_TEXT, chunk_size=50)

    assert len(chunks) > 1
    assert all(len(chunk) <= 50 for chunk in chunks)


def test_overlap_chunking():

    chunks = overlap_chunking(SAMPLE_TEXT, chunk_size=80, overlap=20)

    assert len(chunks) > 1
    assert all(len(chunk) <= 80 for chunk in chunks)


def test_paragraph_chunking():

    chunks = paragraph_chunking(SAMPLE_TEXT)

    assert len(chunks) >= 2
    assert "Company Travel Policy" in chunks[0]


def test_sentence_chunking():

    chunks = sentence_chunking(SAMPLE_TEXT)

    assert len(chunks) >= 2
    assert any("Visa processing fees" in chunk for chunk in chunks)


def test_chunk_text_strategy_router():

    chunks = chunk_text(
        SAMPLE_TEXT,
        "Sentence chunking",
        chunk_size=100,
        overlap=20
    )

    assert len(chunks) >= 2


def test_retrieve_best_chunk():

    chunks = sentence_chunking(SAMPLE_TEXT)

    best_chunk, score, scored_chunks = retrieve_best_chunk(
        "Can I claim visa processing fees?",
        chunks
    )

    assert best_chunk is not None
    assert "Visa processing fees" in best_chunk
    assert score > 0
    assert len(scored_chunks) > 0


def test_generate_demo_answer():

    answer = generate_demo_answer(
        "Can I claim visa fees?",
        "Visa processing fees are reimbursable with manager approval."
    )

    assert "Visa processing fees" in answer


def test_explain_strategy():

    explanation = explain_strategy("Overlap chunking")

    assert "context" in explanation.lower()