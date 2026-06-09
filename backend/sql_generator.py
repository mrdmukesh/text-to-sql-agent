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
    # PRIORITY LOGIC
    # -----------------------------
    if uploaded_schema and uploaded_schema.strip():
         full_schema = f"""
        YOU ARE QUERYING A DATABASE SYSTEM WITH TWO DATA SOURCES.

        DEFAULT DATABASE TABLES:
        {static_schema}

        USER-UPLOADED DATABASE TABLES:
        {uploaded_schema}

        IMPORTANT RULES:
        - Use employees table for employee-related questions.
        - Use uploaded tables for uploaded CSV related questions.
        - ONLY use tables present in the schemas above.
        - Use proper JOINs when relationships exist.
        - Generate only valid SQLite SELECT SQL.
        - Return only SQL query.
        """
    else:
          full_schema = f"""
            YOU ARE QUERYING A STATIC DATABASE.

            DATABASE SCHEMA:
            {static_schema}
"""

    # -----------------------------
    # BUILD PROMPT
    # -----------------------------
    prompt = SQL_PROMPT.format(
        schema=full_schema,
        question=question
    )

    # -----------------------------
    # CALL OPENAI
    # -----------------------------
    sql, usage = call_openai(
        prompt,
        return_usage=True
    )

    sql = (
        sql.strip()
        .replace("```sql", "")
        .replace("```", "")
        .strip()
    )

    return sql, usage