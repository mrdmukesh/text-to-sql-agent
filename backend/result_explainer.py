from backend.llm_engine import call_openai


def explain_result(question, sql, rows):

    prompt = f"""
User Question:
{question}

Generated SQL:
{sql}

Query Result:
{rows}

Provide a short natural language answer.

Rules:
1. Answer in plain English.
2. Do not mention SQL.
3. Keep answer under 2 sentences.
4. If no rows found, say no matching records were found.
5. Do not assume any currency unless explicitly provided.
6. Base the answer only on the query result provided.
"""

    return call_openai(prompt)