"""
Streamlit UI for Text-to-SQL Agent
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

# ---------- Initialize DB ----------
init_db()

# ---------- Page Config ----------
st.set_page_config(
    page_title="Text-to-SQL AI Agent",
    page_icon="🗄️",
    layout="wide"
)

# ---------- Header ----------
st.title("🧠 Text to SQL AI Agent")
st.markdown("Ask questions in natural language and get SQL results instantly")

# ---------- Session State ----------
if "chat" not in st.session_state:
    st.session_state.chat = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# ---------- Sidebar ----------
with st.sidebar:

    st.header("📌 Sample Queries")

    samples = [
        "show all employees",
        "show IT employees",
        "salary > 70000",
        "count employees"
    ]

    for q in samples:
        if st.button(q):
            st.session_state.pending_question = q
            st.rerun()

    st.markdown("---")

    st.subheader("📐 Schema")
    st.code(load_schema(), language="text")

    if st.button("🧹 Clear Chat"):
        st.session_state.chat = []
        st.rerun()

# ---------- Show Chat History ----------
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------- Input Handling ----------
query = None

if st.session_state.get("pending_question"):
    query = st.session_state.pending_question
    st.session_state.pending_question = None

user_input = st.chat_input("Ask a question about your database...")

if user_input:
    query = user_input

# ---------- Process Query ----------
if query:

    # Show user message
    st.session_state.chat.append({
        "role": "user",
        "content": query
    })

    with st.chat_message("user"):
        st.write(query)

    # ---------- Generate SQL ----------
    sql = generate_sql(query)
    sql = sql.strip().replace("```sql", "").replace("```", "")

    with st.chat_message("assistant"):
        st.markdown("### 🧠 Generated SQL")
        st.code(sql, language="sql")

    # ---------- Execute SQL ----------
    result = run_sql(sql)

    # ---------- Generate Natural Language Answer ----------
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

    # ---------- Display Results ----------
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

                st.markdown("### 📊 Query Result")
                st.write(f"Rows Returned: {len(df)}")

                st.dataframe(
                    df,
                    use_container_width=True
                )

            else:
                st.info("No records found.")

    # ---------- Save History ----------
    save_history(
        query,
        sql,
        result
    )