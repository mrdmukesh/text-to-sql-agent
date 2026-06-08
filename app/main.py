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
from services.file_upload_service import (
    save_csv_to_sqlite,
    get_uploaded_schema,
    UPLOAD_DB
)

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
    🧠 AI Data Analyst
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center;'>Upload CSV files or query your database using natural language.</p>",
    unsafe_allow_html=True
)

# ---------------- SESSION ----------------
if "chat" not in st.session_state:
    st.session_state.chat = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    if st.button("🗑️ Clear Uploaded Data"):
        if os.path.exists(UPLOAD_DB):
            os.remove(UPLOAD_DB)
            st.success("Uploaded data cleared.")
            st.rerun()
        else:
            st.info("No uploaded data found.")

    st.title("📂 Data Control Panel")

    uploaded_files = st.file_uploader(
        "Upload one or more CSV files",
        type=["csv"],
        accept_multiple_files=True
    )

    if uploaded_files:

        for uploaded_file in uploaded_files:

            try:
                uploaded_file.seek(0)

                table_name, columns = save_csv_to_sqlite(uploaded_file)

                st.success(f"Uploaded: {uploaded_file.name}")
                st.write(f"Created table: `{table_name}`")
                st.write("Columns:")
                st.write(columns)

                uploaded_file.seek(0)
                df_preview = pd.read_csv(uploaded_file)

                with st.expander(f"Preview {uploaded_file.name}"):
                    st.dataframe(df_preview)

            except Exception as e:
                st.error(f"Upload failed for {uploaded_file.name}: {str(e)}")

    st.markdown("---")

    st.subheader("📌 Sample Queries")

    samples = [
        "Where does Mukesh Dabi live?",
        "Show all persons with their city",
        "Show Mukesh Dabi contact details",
        "Which person lives in Bangalore?",
        "show all employees"
    ]

    for q in samples:
        if st.button(q):
            st.session_state.pending_question = q
            st.rerun()

    st.markdown("---")

    st.subheader("📐 Database Schema")

    current_schema = load_schema() + "\n" + get_uploaded_schema()
    st.code(current_schema, language="text")

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

    st.session_state.chat.append(
        {
            "role": "user",
            "content": query
        }
    )

    with st.chat_message("user"):
        st.write(query)

    # ---------------- GENERATE SQL ----------------
    sql = generate_sql(query)
    sql = sql.strip().replace("```sql", "").replace("```", "").strip()

    with st.chat_message("assistant"):
        st.markdown("### 🧠 Generated SQL")
        st.code(sql, language="sql")

    # ---------------- EXECUTE SQL ----------------
    result = run_sql(sql)

    # ---------------- NATURAL LANGUAGE ANSWER ----------------
    answer = ""

    if "error" not in result:
        try:
            answer = explain_result(
                query,
                sql,
                result["rows"]
            )
        except Exception as e:
            answer = f"Unable to generate explanation: {str(e)}"

    # ---------------- DISPLAY RESULT ----------------
    with st.chat_message("assistant"):

        if answer:
            st.markdown("### 🤖 Answer")
            st.success(answer)

        if "error" in result:
            st.error(result["error"])

        else:
            rows = result["rows"]
            columns = result["columns"]

            if rows:
                df = pd.DataFrame(
                    rows,
                    columns=columns
                )

                st.markdown("### 📊 Result")
                st.write(f"Rows: {len(df)}")
                st.dataframe(df)

            else:
                st.info("No data found")

    # ---------------- SAVE HISTORY ----------------
    save_history(
        query,
        sql,
        result
    )