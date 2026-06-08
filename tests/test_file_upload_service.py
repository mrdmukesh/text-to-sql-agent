import pandas as pd
from services.file_upload_service import save_csv_to_sqlite
import sqlite3


def test_save_csv_to_sqlite(tmp_path):

    # Create sample dataframe
    df = pd.DataFrame({
        "student_id": [1, 2],
        "name": ["A", "B"],
        "marks": [90, 80]
    })

    # Save temp CSV
    file_path = tmp_path / "test.csv"
    df.to_csv(file_path, index=False)

    # Open file like Streamlit upload
    with open(file_path, "rb") as f:
        columns = save_csv_to_sqlite(f)

    # ---------- Assertions ----------
    assert "student_id" in columns
    assert "name" in columns
    assert "marks" in columns

def test_uploaded_data_exists(tmp_path):

    import os

    df = pd.DataFrame({
        "student_id": [1],
        "name": ["A"],
        "marks": [90]
    })

    file_path = tmp_path / "test.csv"
    df.to_csv(file_path, index=False)

    with open(file_path, "rb") as f:
        save_csv_to_sqlite(f)

    conn = sqlite3.connect("uploads/uploaded_data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    conn.close()

    assert any("uploaded_data" in t[0] for t in tables)