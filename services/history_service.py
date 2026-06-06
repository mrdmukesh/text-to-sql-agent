import sqlite3
from config.settings import DB_PATH

def save_history(question, sql, result):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            sql TEXT,
            result TEXT
        )
    """)

    cur.execute("""
        INSERT INTO history (question, sql, result)
        VALUES (?, ?, ?)
    """, (question, sql, str(result)))

    conn.commit()
    conn.close()