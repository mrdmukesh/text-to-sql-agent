import os
import sqlite3
from config.settings import DB_PATH as DEFAULT_DB_PATH

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
UPLOAD_DB_PATH = os.path.join(UPLOADS_DIR, "uploaded_data.db")


def get_uploaded_tables():

    if not os.path.exists(UPLOAD_DB_PATH):
        return []

    conn = sqlite3.connect(UPLOAD_DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )

    tables = [
        row[0].lower()
        for row in cursor.fetchall()
    ]

    conn.close()

    return tables


def get_db_path(query: str):

    query_lower = str(query).lower()

    uploaded_tables = get_uploaded_tables()

    for table in uploaded_tables:

        if table in query_lower:
            return UPLOAD_DB_PATH

    return DEFAULT_DB_PATH


def run_sql(query: str):

    conn = None

    try:

        query = str(query).strip()

        db_path = get_db_path(query)

        forbidden = [
            "DROP",
            "DELETE",
            "UPDATE",
            "INSERT",
            "ALTER",
            "TRUNCATE",
            "CREATE"
        ]

        upper_query = query.upper()

        if any(word in upper_query for word in forbidden):

            return {
                "error": "Only SELECT queries are allowed."
            }

        if not upper_query.startswith("SELECT"):

            return {
                "error": "Only SELECT queries are allowed."
            }

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(query)

        rows = cursor.fetchall()

        columns = (
            [desc[0] for desc in cursor.description]
            if cursor.description
            else []
        )

        return {
            "columns": columns,
            "rows": rows
        }

    except Exception as e:

        return {
            "error": f"Execution Error: {str(e)}"
        }

    finally:

        if conn:
            conn.close()