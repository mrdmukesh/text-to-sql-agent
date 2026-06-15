import os
import re
import pandas as pd
import pyodbc
from dotenv import load_dotenv
from langsmith import traceable

from backend.llm_engine import call_openai

load_dotenv()


def get_connection_string():
    conn_str = os.getenv("AZURE_SQL_CONNECTION_STRING")

    if not conn_str:
        raise ValueError("AZURE_SQL_CONNECTION_STRING is missing.")

    return conn_str


@traceable(name="Get Azure SQL Schema")
def get_azure_sql_schema():
    conn = pyodbc.connect(get_connection_string())
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo'
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """)

    rows = cursor.fetchall()
    conn.close()

    schema = {}

    for table_name, column_name, data_type in rows:
        schema.setdefault(table_name, []).append(f"{column_name} {data_type}")

    schema_text = ""

    for table, columns in schema.items():
        schema_text += f"\nTable: {table}\n"
        schema_text += "Columns: " + ", ".join(columns) + "\n"

    return schema_text


def clean_sql(sql_text):
    sql_text = sql_text.strip()
    sql_text = re.sub(r"```sql", "", sql_text, flags=re.IGNORECASE)
    sql_text = re.sub(r"```", "", sql_text)
    return sql_text.strip()


def validate_select_only(sql):
    sql_lower = sql.lower().strip()

    blocked = [
        "insert", "update", "delete", "drop", "alter",
        "truncate", "merge", "create", "exec", "execute"
    ]

    if not sql_lower.startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")

    for keyword in blocked:
        if re.search(rf"\b{keyword}\b", sql_lower):
            raise ValueError(f"Blocked unsafe SQL keyword: {keyword}")

    return True


@traceable(name="Generate Azure SQL Query")
def generate_azure_sql(question):
    schema = get_azure_sql_schema()

    prompt = f"""
You are an expert Azure SQL Server analyst.

Generate ONLY one safe SELECT query for Azure SQL Database.

Rules:
- Use only tables and columns from the schema.
- Return only SQL, no explanation.
- Do not use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, MERGE, EXEC.
- Use TOP instead of LIMIT.
- Use SQL Server syntax.

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

SQL:
"""

    sql = call_openai(prompt)
    sql = clean_sql(sql)
    validate_select_only(sql)

    return sql


@traceable(name="Execute Azure SQL Query")
def execute_azure_sql(sql):
    validate_select_only(sql)

    conn = pyodbc.connect(get_connection_string())
    df = pd.read_sql(sql, conn)
    conn.close()

    return df