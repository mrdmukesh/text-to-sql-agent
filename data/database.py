import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        department TEXT,
        salary INTEGER
    )
    """)

    cursor.execute("""INSERT OR IGNORE INTO employees (id, name, department, salary)VALUES (1, 'Amit', 'IT', 90000)""")
    cursor.execute("""INSERT OR IGNORE INTO employees (id, name, department, salary)VALUES (2, 'Ravi', 'HR', 60000)""")
    cursor.execute("""INSERT OR IGNORE INTO employees (id, name, department, salary) VALUES (3, 'Neha', 'Finance', 75000)""")
    
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            sql TEXT,
            result TEXT
        )
        """)

    conn.commit()
    conn.close()