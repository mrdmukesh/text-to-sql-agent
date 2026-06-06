import sqlite3
from config.settings import DB_PATH


def run_sql(query: str):
    #print("SQL_EXECUTOR.PY LOADED")
    #print("===== RUN_SQL CALLED =====")
    #print("QUERY =", query)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:

        query = query.strip()

        #print(f"SQL RECEIVED: {query}")

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

            #print(f"BLOCKED SQL: {query}")

            return {
                "error": "Only SELECT queries are allowed."
            }

        if not upper_query.startswith("SELECT"):

            #print(f"NON-SELECT BLOCKED: {query}")

            return {
                "error": "Only SELECT queries are allowed."
            }

        cursor.execute(query)

        rows = cursor.fetchall()

        columns = (
            [desc[0] for desc in cursor.description]
            if cursor.description
            else []
        )
        #print("ROWS =", rows)
        #print("COLUMNS =", columns)

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