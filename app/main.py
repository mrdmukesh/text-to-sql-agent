"""
Text-to-SQL AI Agent (Professional Version)
"""

import sys
import os
import streamlit as st
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.sql_generator import generate_sql
from backend.sql_executor import run_sql
from backend.result_explainer import explain_result
from data.database import init_db
from services.history_service import save_history
from backend.schema_loader import load_schema
from services.file_upload_service import save_csv_to_sqlite, get_uploaded_schema


# ---------------- INIT ----------------
init_db()

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="🧠",
    layout="wide"
)

# ---------------- HEADER ----------------
st.markdown(
    """
    <h1 style='text-align: center; color: #4A90E2;'>
    🧠 AI Data Analyst (Text → SQL)
    </h1>
    """,
    unsafe_allow_html=True
)

st.caption("Upload data or query your database using natural language")

# ---------------- SESSION ----------------
if "chat" not in st.session_state:
    st.session_state.chat = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.title("📂 Data Control Panel")

    uploaded_file = st.file_uploader(
        "Upload CSV File",
        type=["csv"]
    )

    if uploaded_file is not None:
        try:
            uploaded_file.seek(0)

            df = pd.read_csv(uploaded_file)

            st.success("File Loaded Successfully")

            st.subheader("Preview")
            st.dataframe(df, use_container_width=True)

            uploaded_file.seek(0)
            cols = save_csv_to_sqlite(uploaded_file)

            st.subheader("Detected Columns")
            st.write(cols)

        except Exception as e:
            st.error(f"Upload Error: {str(e)}")

    st.markdown("---")

    st.subheader("📌 Sample Queries")

    samples = [
        "show all students",
        "students with marks greater than 80",
        "average marks",
        "count students"
    ]

    for q in samples:
        if st.button(q):
            st.session_state.pending_question = q
            st.rerun()

    st.markdown("---")

    st.subheader("📐 Database Schema")
    st.code(load_schema() + "\n" + get_uploaded_schema(), language="text")

    if st.button("🧹 Clear Chat"):
        st.session_state.chat = []
        st.rerun()


# =========================================================
# CHAT HISTORY
# =========================================================
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# =========================================================
# INPUT
# =========================================================
query = None

if st.session_state.get("pending_question"):
    query = st.session_state.pending_question
    st.session_state.pending_question = None

user_input = st.chat_input("Ask your data question...")

if user_input:
    query = user_input


# =========================================================
# PROCESS QUERY
# =========================================================
if query:

    st.session_state.chat.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.write(query)

    # ---------------- SQL GENERATION (FIX HERE) ----------------
    static_schema = load_schema()
    dynamic_schema = get_uploaded_schema()

    full_schema = static_schema + "\n" + dynamic_schema

    sql = generate_sql(query)
    sql = sql.strip().replace("```sql", "").replace("```", "")

    with st.chat_message("assistant"):
        st.markdown("### 🧠 Generated SQL")
        st.code(sql, language="sql")

    # ---------------- EXECUTE ----------------
    result = run_sql(sql)

    answer = ""

    if "error" not in result:
        try:
            answer = explain_result(query, sql, result["rows"])
        except Exception as e:
            answer = str(e)

    with st.chat_message("assistant"):

        if answer:
            st.markdown("### 🤖 Answer")
            st.success(answer)

        if "error" in result:
            st.error(result["error"])
        else:
            rows = result["rows"]
            cols = result["columns"]

            if rows:
                df = pd.DataFrame(rows, columns=cols)
                st.markdown("### 📊 Result")
                st.write(f"Rows: {len(df)}")
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No data found")

    save_history(query, sql, result)