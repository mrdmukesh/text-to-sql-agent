import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
HISTORY_DB = os.path.join(BASE_DIR, "data", "history.db")


def get_history_connection():
    os.makedirs(os.path.dirname(HISTORY_DB), exist_ok=True)
    return sqlite3.connect(HISTORY_DB)


def init_history_db():
    conn = get_history_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_email TEXT,
        question TEXT,
        sql_query TEXT,
        answer TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_history(user_id, user_email, question, sql_query, answer, status):
    conn = get_history_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO chat_history (
        user_id, user_email, question, sql_query, answer, status, created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        user_email,
        question,
        sql_query,
        answer,
        status,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_user_history(user_id, limit=20):
    conn = get_history_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT question, sql_query, answer, status, created_at
    FROM chat_history
    WHERE user_id = ?
    ORDER BY id DESC
    LIMIT ?
    """, (user_id, limit))

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_history(limit=50):
    conn = get_history_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT user_email, question, sql_query, status, created_at
    FROM chat_history
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows

def get_history_analytics():
    conn = get_history_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM chat_history")
    total_queries = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE status = 'success'")
    successful_queries = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE status = 'error'")
    failed_queries = cursor.fetchone()[0]

    cursor.execute("""
    SELECT user_email, COUNT(*) as query_count
    FROM chat_history
    GROUP BY user_email
    ORDER BY query_count DESC
    LIMIT 5
    """)
    top_users = cursor.fetchall()

    conn.close()

    return {
        "total_queries": total_queries,
        "successful_queries": successful_queries,
        "failed_queries": failed_queries,
        "top_users": top_users
    }