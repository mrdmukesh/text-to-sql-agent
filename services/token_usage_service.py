import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
USAGE_DB = os.path.join(BASE_DIR, "data", "usage.db")


def get_usage_connection():
    os.makedirs(os.path.dirname(USAGE_DB), exist_ok=True)
    return sqlite3.connect(USAGE_DB)


def init_usage_db():
    conn = get_usage_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS token_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_email TEXT,
        feature TEXT,
        prompt_tokens INTEGER,
        completion_tokens INTEGER,
        total_tokens INTEGER,
        estimated_cost REAL,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def estimate_cost(total_tokens):
    # rough estimate for demo only
    return round((total_tokens / 1000) * 0.0002, 6)


def save_token_usage(user_id, user_email, feature, usage):
    conn = get_usage_connection()
    cursor = conn.cursor()

    total_tokens = usage.get("total_tokens", 0)

    cursor.execute("""
    INSERT INTO token_usage (
        user_id,
        user_email,
        feature,
        prompt_tokens,
        completion_tokens,
        total_tokens,
        estimated_cost,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        user_email,
        feature,
        usage.get("prompt_tokens", 0),
        usage.get("completion_tokens", 0),
        total_tokens,
        estimate_cost(total_tokens),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_user_token_usage(user_id):
    conn = get_usage_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        COALESCE(SUM(total_tokens), 0),
        COALESCE(SUM(estimated_cost), 0)
    FROM token_usage
    WHERE user_id = ?
    """, (user_id,))

    row = cursor.fetchone()
    conn.close()

    return {
        "total_tokens": row[0],
        "estimated_cost": row[1]
    }


def get_all_token_usage():
    conn = get_usage_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        user_email,
        COUNT(*) as calls,
        COALESCE(SUM(total_tokens), 0) as total_tokens,
        COALESCE(SUM(estimated_cost), 0) as estimated_cost
    FROM token_usage
    GROUP BY user_email
    ORDER BY total_tokens DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows