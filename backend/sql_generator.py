from backend.llm_engine import call_openai
from backend.schema_loader import load_schema
from models.prompts import SQL_PROMPT
from services.file_upload_service import get_uploaded_schema


def generate_sql(question: str):

    # -----------------------------
    # LOAD SCHEMAS
    # -----------------------------
    static_schema = load_schema()
    uploaded_schema = get_uploaded_schema()

    # -----------------------------
    # BUILD ACTIVE SCHEMA
    # -----------------------------
    if uploaded_schema and "uploaded_data" in uploaded_schema:

        full_schema = f"""
YOU ARE A STRICT SQL GENERATION ENGINE.

YOU MUST FOLLOW THESE RULES:
- ONLY USE TABLE: uploaded_data
- NEVER invent tables like employees, sales, etc.
- NEVER say "unable to answer"
- ALWAYS return valid SQL

SCHEMA:
{uploaded_schema}

EXAMPLES:
Question: show all students
SQL: SELECT * FROM uploaded_data;

Question: marks greater than 80
SQL: SELECT * FROM uploaded_data WHERE marks > 80;
"""

    else:

        full_schema = f"""
YOU ARE A STRICT SQL GENERATION ENGINE.

RULES:
- ONLY USE GIVEN SCHEMA
- RETURN ONLY SQL QUERY

SCHEMA:
{static_schema}
"""

    # -----------------------------
    # STRICT PROMPT
    # -----------------------------
    prompt = SQL_PROMPT.format(
        schema=full_schema,
        question=question
    )

    # -----------------------------
    # CALL LLM
    # -----------------------------
    sql = call_openai(prompt)

    # -----------------------------
    # SAFETY CLEANUP (IMPORTANT)
    # -----------------------------
    sql = sql.strip().replace("```sql", "").replace("```", "")

    # block hallucinated fallback answers
    if "unable" in sql.lower():
        return "SELECT * FROM uploaded_data"

    return sql