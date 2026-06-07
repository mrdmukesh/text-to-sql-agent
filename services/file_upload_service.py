import sqlite3
import pandas as pd
import os

UPLOAD_DB = "uploads/uploaded_data.db"


def save_csv_to_sqlite(uploaded_file):

    os.makedirs("uploads", exist_ok=True)

    df = pd.read_csv(uploaded_file)

    conn = sqlite3.connect(UPLOAD_DB)

    df.to_sql(
        "uploaded_data",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    return list(df.columns)