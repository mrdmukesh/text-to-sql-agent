from backend.llm_engine import call_openai
from backend.schema_loader import load_schema
from models.prompts import SQL_PROMPT
from services.file_upload_service import get_uploaded_schema


def generate_sql(question: str):

    static_schema = load_schema()
    uploaded_schema = get_uploaded_schema()

    full_schema = f"""
YOU ARE A STRICT SQLITE SQL GENERATOR.

AVAILABLE DATABASE TABLES:

DEFAULT TABLES:
{static_schema}

UPLOADED TABLES:
{uploaded_schema}

IMPORTANT RULES:
1. Use ONLY available tables.
2. employees table belongs to default database.
3. uploaded tables belong to uploaded database.
4. Return ONLY SELECT SQL.
5. Never explain anything.
6. Use JOIN when relationships exist.
7. Use LOWER(column)=LOWER(value) for text matching.

RELATIONSHIP EXAMPLES:
persons.person_id = addresses.person_id
persons.person_id = contacts.person_id
"""

    prompt = SQL_PROMPT.format(
        schema=full_schema,
        question=question
    )

    sql = call_openai(prompt)

    sql = (
        sql
        .strip()
        .replace("```sql", "")
        .replace("```", "")
        .strip()
    )

    return sql