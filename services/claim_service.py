import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CLAIM_DB = os.path.join(BASE_DIR, "data", "claims.db")


def get_claim_connection():
    os.makedirs(os.path.dirname(CLAIM_DB), exist_ok=True)
    return sqlite3.connect(CLAIM_DB)


def init_claim_db():
    conn = get_claim_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_email TEXT,
        vendor_name TEXT,
        receipt_date TEXT,
        amount TEXT,
        currency TEXT,
        tax_amount TEXT,
        category TEXT,
        payment_method TEXT,
        invoice_number TEXT,
        description TEXT,
        confidence_score TEXT,
        status TEXT DEFAULT 'Draft',
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_claim(user_id, user_email, claim_data):
    conn = get_claim_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO claims (
        user_id,
        user_email,
        vendor_name,
        receipt_date,
        amount,
        currency,
        tax_amount,
        category,
        payment_method,
        invoice_number,
        description,
        confidence_score,
        status,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        user_email,
        claim_data.get("vendor_name", ""),
        claim_data.get("receipt_date", ""),
        claim_data.get("amount", ""),
        claim_data.get("currency", ""),
        claim_data.get("tax_amount", ""),
        claim_data.get("category", ""),
        claim_data.get("payment_method", ""),
        claim_data.get("invoice_number", ""),
        claim_data.get("description", ""),
        claim_data.get("confidence_score", ""),
        claim_data.get("status", "Draft"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_user_claims(user_id):
    conn = get_claim_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, vendor_name, receipt_date, amount, currency, category, status, created_at
    FROM claims
    WHERE user_id = ?
    ORDER BY id DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_claims():
    conn = get_claim_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, user_email, vendor_name, receipt_date, amount, currency, category, status, created_at
    FROM claims
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def update_claim_status(claim_id, status):
    conn = get_claim_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE claims
    SET status = ?
    WHERE id = ?
    """, (status, claim_id))

    conn.commit()
    conn.close()