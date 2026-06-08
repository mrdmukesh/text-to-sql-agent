import sqlite3
import pandas as pd

from services.file_upload_service import (
    save_csv_to_sqlite,
    UPLOAD_DB
)


def test_save_csv_to_sqlite(tmp_path):

    df = pd.DataFrame({
        "student_id": [1, 2],
        "name": ["A", "B"],
        "marks": [90, 80]
    })

    file_path = tmp_path / "students.csv"

    df.to_csv(file_path, index=False)

    with open(file_path, "rb") as f:

        table_name, columns = save_csv_to_sqlite(f)

    # ---------- ASSERTIONS ----------
    assert "students" in table_name
    assert "student_id" in columns
    assert "name" in columns
    assert "marks" in columns


def test_uploaded_table_exists(tmp_path):

    df = pd.DataFrame({
        "student_id": [1],
        "name": ["A"],
        "marks": [90]
    })

    file_path = tmp_path / "students.csv"

    df.to_csv(file_path, index=False)

    with open(file_path, "rb") as f:

        table_name, columns = save_csv_to_sqlite(f)

    conn = sqlite3.connect(UPLOAD_DB)

    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )

    tables = cursor.fetchall()

    conn.close()

    assert any(
        table_name == t[0]
        for t in tables
    )