import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "uploads", "uploaded_data.db")


def run_sql(query: str):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        query = query.strip()

        if not query.upper().startswith("SELECT"):
            return {"error": "Only SELECT allowed"}

        cursor.execute(query)

        rows = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description] if cursor.description else []

        return {
            "rows": rows,
            "columns": columns
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        conn.close()