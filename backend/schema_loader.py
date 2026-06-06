import sqlite3
from config.settings import DB_PATH


def load_schema():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    schema_text = ""

    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()

    for table in tables:

        table_name = table[0]

        columns = cursor.execute(
            f"PRAGMA table_info({table_name})"
        ).fetchall()

        schema_text += f"\nTable: {table_name}\n"

        schema_text += "Columns: "

        schema_text += ", ".join(
            [col[1] for col in columns]
        )

        schema_text += "\n"

    conn.close()
    #print("===== SCHEMA LOADER OUTPUT =====")
    #print(schema_text)
    #print("================================")
    return schema_text