import sqlite3
import os
from config.settings import DB_PATH as DEFAULT_DB_PATH

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_DB_PATH = os.path.join(BASE_DIR, "uploads", "uploaded_data.db")


def get_db_path(query: str):
    query_lower = query.lower()

    if "uploaded_data" in query_lower:
        return UPLOAD_DB_PATH

    return DEFAULT_DB_PATH


def run_sql(query: str):

    query = query.strip()
    db_path = get_db_path(query)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
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
            return {"error": "Only SELECT queries are allowed."}

        if not upper_query.startswith("SELECT"):
            return {"error": "Only SELECT queries are allowed."}

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
        conn.close()