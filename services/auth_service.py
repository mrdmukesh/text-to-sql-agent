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
        query_limit INTEGER DEFAULT 5,
        query_count INTEGER DEFAULT 0,
        is_unlocked INTEGER DEFAULT 0,
        plan TEXT DEFAULT 'free'
    )
    """)

    # Migration for existing auth.db where table already exists
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [col[1] for col in cursor.fetchall()]

    columns_to_add = [
        ("query_limit", "INTEGER DEFAULT 5"),
        ("query_count", "INTEGER DEFAULT 0"),
        ("is_unlocked", "INTEGER DEFAULT 0"),
        ("plan", "TEXT DEFAULT 'free'")
    ]

    for column_name, column_type in columns_to_add:
        if column_name not in existing_columns:
            cursor.execute(
                f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
            )

    # Make sure old users get correct default values
    cursor.execute("""
    UPDATE users
    SET query_limit = 5
    WHERE query_limit IS NULL
    """)

    cursor.execute("""
    UPDATE users
    SET query_count = 0
    WHERE query_count IS NULL
    """)

    cursor.execute("""
    UPDATE users
    SET is_unlocked = 0
    WHERE is_unlocked IS NULL
    """)

    cursor.execute("""
    UPDATE users
    SET plan = 'free'
    WHERE plan IS NULL
    """)

    conn.commit()
    conn.close()


def register_user(name, email, password):
    conn = get_auth_connection()
    cursor = conn.cursor()

    email = email.lower()

    role = (
        "admin"
        if email in [e.lower() for e in ADMIN_EMAILS]
        else "user"
    )

    # Admin can get higher/unlocked access
    query_limit = 9999 if role == "admin" else 5
    is_unlocked = 1 if role == "admin" else 0
    plan = "admin" if role == "admin" else "free"

    try:
        cursor.execute("""
        INSERT INTO users (
            name,
            email,
            password_hash,
            role,
            query_limit,
            query_count,
            is_unlocked,
            plan
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            email,
            hash_password(password),
            role,
            query_limit,
            0,
            is_unlocked,
            plan
        ))

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
    SELECT
        id,
        name,
        email,
        role,
        is_active,
        query_limit,
        query_count,
        is_unlocked,
        plan
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
        "query_count": user[6],
        "is_unlocked": bool(user[7]),
        "plan": user[8]
    }, "Login successful."


def can_run_query(user):
    return (
        user["role"] == "admin"
        or user.get("is_unlocked", False)
        or user.get("query_count", 0) < user.get("query_limit", 5)
    )


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
    SELECT
        id,
        name,
        email,
        role,
        is_active,
        query_limit,
        query_count,
        is_unlocked,
        plan
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


def unlock_user(user_id, query_limit=100, plan="unlocked"):
    conn = get_auth_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET
        is_unlocked = 1,
        query_limit = ?,
        plan = ?
    WHERE id = ?
    """, (query_limit, plan, user_id))

    conn.commit()
    conn.close()


def lock_user(user_id):
    conn = get_auth_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET
        is_unlocked = 0,
        query_limit = 5,
        plan = 'free'
    WHERE id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def reset_user_usage(user_id):
    conn = get_auth_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET query_count = 0
    WHERE id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def get_or_create_google_user(name, email):
    conn = get_auth_connection()
    cursor = conn.cursor()

    email = email.lower()

    cursor.execute("""
    SELECT
        id,
        name,
        email,
        role,
        is_active,
        query_limit,
        query_count,
        is_unlocked,
        plan
    FROM users
    WHERE email = ?
    """, (email,))

    user = cursor.fetchone()

    if user:
        conn.close()

        if user[4] == 0:
            return None, "Your account is blocked. Please contact admin."

        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "role": user[3],
            "is_active": user[4],
            "query_limit": user[5],
            "query_count": user[6],
            "is_unlocked": bool(user[7]),
            "plan": user[8]
        }, "Google login successful."

    role = (
        "admin"
        if email in [e.lower() for e in ADMIN_EMAILS]
        else "user"
    )

    query_limit = 9999 if role == "admin" else 5
    is_unlocked = 1 if role == "admin" else 0
    plan = "admin" if role == "admin" else "free"

    cursor.execute("""
    INSERT INTO users (
        name,
        email,
        password_hash,
        role,
        query_limit,
        query_count,
        is_unlocked,
        plan
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        email,
        "GOOGLE_AUTH_USER",
        role,
        query_limit,
        0,
        is_unlocked,
        plan
    ))

    conn.commit()

    cursor.execute("""
    SELECT
        id,
        name,
        email,
        role,
        is_active,
        query_limit,
        query_count,
        is_unlocked,
        plan
    FROM users
    WHERE email = ?
    """, (email,))

    new_user = cursor.fetchone()
    conn.close()

    return {
        "id": new_user[0],
        "name": new_user[1],
        "email": new_user[2],
        "role": new_user[3],
        "is_active": new_user[4],
        "query_limit": new_user[5],
        "query_count": new_user[6],
        "is_unlocked": bool(new_user[7]),
        "plan": new_user[8]
    }, "Google user created and logged in."


def get_user_analytics():
    conn = get_auth_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
    active_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 0")
    blocked_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    admin_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE is_unlocked = 1")
    unlocked_users = cursor.fetchone()[0]

    conn.close()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "blocked_users": blocked_users,
        "admin_users": admin_users,
        "unlocked_users": unlocked_users
    }