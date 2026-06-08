import os
import re
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
UPLOAD_DB = os.path.join(UPLOADS_DIR, "uploaded_data.db")


def clean_table_name(filename: str):
    name = os.path.splitext(os.path.basename(filename))[0]
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    return name.lower()


def save_csv_to_sqlite(uploaded_file):

    os.makedirs(UPLOADS_DIR, exist_ok=True)

    table_name = clean_table_name(uploaded_file.name)

    df = pd.read_csv(uploaded_file)

    conn = sqlite3.connect(UPLOAD_DB)

    df.to_sql(
        table_name,
        conn,
        if_exists="replace",
        index=False
    )

    conn.commit()
    conn.close()

    return table_name, list(df.columns)


def get_uploaded_schema():

    if not os.path.exists(UPLOAD_DB):
        return ""

    conn = sqlite3.connect(UPLOAD_DB)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    schema_text = ""

    for table in tables:
        table_name = table[0]

        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        col_names = [col[1] for col in columns]

        schema_text += f"\nTable: {table_name}\n"
        schema_text += f"Columns: {', '.join(col_names)}\n"

    conn.close()

    return schema_text