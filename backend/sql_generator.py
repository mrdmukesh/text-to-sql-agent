from backend.llm_engine import call_openai
from backend.schema_loader import load_schema
from models.prompts import SQL_PROMPT
from services.file_upload_service import get_uploaded_schema


def generate_sql(question: str):

    static_schema = load_schema()
    uploaded_schema = get_uploaded_schema()

    question_lower = question.lower()

    # Use default employee DB for employee-related questions
    employee_keywords = [
        "employee",
        "employees",
        "department",
        "salary",
        "it employees",
        "hr employees",
        "finance employees"
    ]

    use_static_db = any(keyword in question_lower for keyword in employee_keywords)

    if use_static_db:
        full_schema = f"""
YOU ARE QUERYING THE DEFAULT EMPLOYEE DATABASE.

IMPORTANT RULES:
- Use ONLY the employees table.
- Do NOT use uploaded_data.
- Return ONLY valid SQLite SELECT SQL.

DATABASE SCHEMA:
{static_schema}
"""
    elif uploaded_schema and "uploaded_data" in uploaded_schema:
        full_schema = f"""
YOU ARE QUERYING THE USER-UPLOADED CSV DATABASE.

IMPORTANT RULES:
- Use ONLY the uploaded_data table.
- Do NOT use employees table.
- Return ONLY valid SQLite SELECT SQL.

DATABASE SCHEMA:
{uploaded_schema}

EXAMPLES:
Question: show all students
SQL: SELECT * FROM uploaded_data;

Question: show students with marks greater than 80
SQL: SELECT * FROM uploaded_data WHERE marks > 80;
"""
    else:
        full_schema = f"""
YOU ARE QUERYING THE DEFAULT DATABASE.

IMPORTANT RULES:
- Use ONLY the given schema.
- Return ONLY valid SQLite SELECT SQL.

DATABASE SCHEMA:
{static_schema}
"""

    prompt = SQL_PROMPT.format(
        schema=full_schema,
        question=question
    )

    sql = call_openai(prompt)
    sql = sql.strip().replace("```sql", "").replace("```", "").strip()

    return sql