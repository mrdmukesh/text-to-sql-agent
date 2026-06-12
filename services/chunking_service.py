import re
from collections import Counter


def fixed_size_chunking(text, chunk_size=300):
    return [
        text[i:i + chunk_size].strip()
        for i in range(0, len(text), chunk_size)
        if text[i:i + chunk_size].strip()
    ]


def overlap_chunking(text, chunk_size=300, overlap=80):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += max(chunk_size - overlap, 1)

    return chunks


def paragraph_chunking(text):
    return [
        p.strip()
        for p in text.split("\n\n")
        if p.strip()
    ]


def sentence_chunking(text):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def simple_semantic_chunking(text):
    paragraphs = paragraph_chunking(text)

    if not paragraphs:
        return sentence_chunking(text)

    chunks = []
    current_chunk = ""

    topic_keywords = [
        "travel",
        "visa",
        "hotel",
        "food",
        "reimbursement",
        "approval",
        "policy",
        "personal"
    ]

    for paragraph in paragraphs:
        lower_para = paragraph.lower()

        if any(keyword in lower_para for keyword in topic_keywords):
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            current_chunk += "\n\n" + paragraph

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def chunk_text(text, strategy, chunk_size=300, overlap=80):
    if strategy == "Fixed-size chunking":
        return fixed_size_chunking(text, chunk_size)

    if strategy == "Overlap chunking":
        return overlap_chunking(text, chunk_size, overlap)

    if strategy == "Paragraph chunking":
        return paragraph_chunking(text)

    if strategy == "Sentence chunking":
        return sentence_chunking(text)

    if strategy == "Semantic chunking":
        return simple_semantic_chunking(text)

    return []


def clean_words(text):
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())

    stop_words = {
        "the", "is", "are", "a", "an", "and", "or", "to", "of", "in",
        "on", "for", "with", "when", "can", "i", "me", "my", "it",
        "this", "that", "only", "be", "by", "as", "at", "from"
    }

    return [
        word
        for word in words
        if word not in stop_words
    ]


def score_chunk(question, chunk):
    question_words = clean_words(question)
    chunk_words = clean_words(chunk)

    if not question_words or not chunk_words:
        return 0

    question_counter = Counter(question_words)
    chunk_counter = Counter(chunk_words)

    score = 0

    for word in question_counter:
        if word in chunk_counter:
            score += min(question_counter[word], chunk_counter[word])

    return score


def retrieve_best_chunk(question, chunks):
    if not chunks:
        return None, 0, []

    scored_chunks = []

    for index, chunk in enumerate(chunks, start=1):
        score = score_chunk(question, chunk)

        scored_chunks.append({
            "chunk_number": index,
            "chunk": chunk,
            "score": score
        })

    scored_chunks = sorted(
        scored_chunks,
        key=lambda x: x["score"],
        reverse=True
    )

    best = scored_chunks[0]

    return best["chunk"], best["score"], scored_chunks


def generate_demo_answer(question, retrieved_chunk):
    if not retrieved_chunk:
        return "No relevant chunk was retrieved, so the system cannot answer confidently."

    return (
        "Based on the retrieved chunk, the answer is likely: "
        f"{retrieved_chunk}"
    )


def explain_strategy(strategy):
    explanations = {
        "Fixed-size chunking": (
            "Fixed-size chunking splits text by character length. "
            "It is simple and fast, but it may cut sentences or policies in the middle."
        ),
        "Overlap chunking": (
            "Overlap chunking repeats some text between chunks. "
            "This helps preserve context across chunk boundaries and is a strong default for RAG."
        ),
        "Paragraph chunking": (
            "Paragraph chunking keeps natural document sections together. "
            "It works well for policies, reports, SOPs, and documentation."
        ),
        "Sentence chunking": (
            "Sentence chunking creates very small chunks. "
            "It is useful for FAQs, but it may lose wider context."
        ),
        "Semantic chunking": (
            "Semantic chunking groups text by meaning or topic. "
            "It usually gives better retrieval quality for complex documents."
        )
    }

    return explanations.get(strategy, "")