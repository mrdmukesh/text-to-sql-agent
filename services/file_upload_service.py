import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_DB = os.path.join(BASE_DIR, "uploads", "uploaded_data.db")


def save_csv_to_sqlite(uploaded_file):

    os.makedirs(os.path.dirname(UPLOAD_DB), exist_ok=True)

    df = pd.read_csv(uploaded_file)

    conn = sqlite3.connect(UPLOAD_DB)

    df.to_sql(
        "uploaded_data",
        conn,
        if_exists="replace",
        index=False
    )

    conn.commit()
    conn.close()

    return list(df.columns)


def get_uploaded_schema():

    if not os.path.exists(UPLOAD_DB):
        return ""

    conn = sqlite3.connect(UPLOAD_DB)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(uploaded_data)")
    cols = cursor.fetchall()

    conn.close()

    return f"Table: uploaded_data\nColumns: {[c[1] for c in cols]}"