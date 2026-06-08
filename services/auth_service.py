import sqlite3
import hashlib
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
AUTH_DB = os.path.join(BASE_DIR, "data", "auth.db")

ADMIN_EMAILS = [
    "mrdmukesh@gmail.com",
    "admin_test_unique@gmail.com"
]


def get_auth_connection():
    os.makedirs(os.path.dirname(AUTH_DB), exist_ok=True)
    return sqlite3.connect(AUTH_DB)


def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


def init_auth_db():
    conn = get_auth_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password_hash TEXT,
        role TEXT DEFAULT 'user',
        is_active INTEGER DEFAULT 1,
        query_limit INTEGER DEFAULT 10,
        query_count INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


def register_user(name, email, password):
    conn = get_auth_connection()
    cursor = conn.cursor()

    role = (
    "admin"
    if email.lower() in [e.lower() for e in ADMIN_EMAILS]
    else "user"
)

    try:
        cursor.execute("""
        INSERT INTO users (name, email, password_hash, role)
        VALUES (?, ?, ?, ?)
        """, (name, email.lower(), hash_password(password), role))

        conn.commit()
        return True, "Registration successful."

    except sqlite3.IntegrityError:
        return False, "Email already registered."

    finally:
        conn.close()


def login_user(email, password):
    conn = get_auth_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, email, role, is_active, query_limit, query_count
    FROM users
    WHERE email = ? AND password_hash = ?
    """, (email.lower(), hash_password(password)))

    user = cursor.fetchone()
    conn.close()

    if not user:
        return None, "Invalid email or password."

    if user[4] == 0:
        return None, "Your account is blocked. Please contact admin."

    return {
        "id": user[0],
        "name": user[1],
        "email": user[2],
        "role": user[3],
        "is_active": user[4],
        "query_limit": user[5],
        "query_count": user[6]
    }, "Login successful."


def can_run_query(user):
    return user["role"] == "admin" or user["query_count"] < user["query_limit"]


def increment_query_count(user_id):
    conn = get_auth_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET query_count = query_count + 1
    WHERE id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def get_all_users():
    conn = get_auth_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, email, role, is_active, query_limit, query_count
    FROM users
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def update_user_status(user_id, is_active):
    conn = get_auth_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET is_active = ?
    WHERE id = ?
    """, (is_active, user_id))

    conn.commit()
    conn.close()