import streamlit as st
import pandas as pd

from backend.sql_generator import generate_sql
from backend.sql_executor import run_sql
from backend.result_explainer import explain_result
from backend.schema_loader import load_schema

from services.file_upload_service import get_uploaded_schema
from services.auth_service import can_run_query, increment_query_count
from services.history_service import save_history
from services.token_usage_service import save_token_usage


def render_text_to_sql():

    st.subheader("📊 Text-to-SQL / Chat with Data")

    with st.expander("📐 Current Database Schema", expanded=False):
        current_schema = load_schema() + "\n" + get_uploaded_schema()
        st.code(current_schema, language="text")

    st.markdown("### Suggested Questions")

    samples = [
        "show all employees",
        "Where does Mukesh Dabi live?",
        "Show Mukesh Dabi contact details",
        "Show all persons with their city",
        "Which person lives in Bangalore?"
    ]

    cols = st.columns(len(samples))

    for i, q in enumerate(samples):
        with cols[i]:
            if st.button(q, key=f"sample_{i}"):
                st.session_state.pending_question = q
                st.rerun()

    st.markdown("---")

    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    query = None

    if st.session_state.get("pending_question"):
        query = st.session_state.pending_question
        st.session_state.pending_question = None

    user_input = st.chat_input("Ask your data question...")

    if user_input:
        query = user_input

    if query:
        process_query(query)


def process_query(query):

    if not can_run_query(st.session_state.user):
        st.error("Query limit reached. Please contact admin.")
        st.stop()

    st.session_state.chat.append({
        "role": "user",
        "content": query
    })

    with st.chat_message("user"):
        st.write(query)

    sql, usage = generate_sql(query)
    sql = sql.strip().replace("```sql", "").replace("```", "").strip()

    with st.chat_message("assistant"):
        st.markdown("### 🧠 Generated SQL")
        st.code(sql, language="sql")

    result = run_sql(sql)

    save_token_usage(
        st.session_state.user["id"],
        st.session_state.user["email"],
        "Text-to-SQL",
        usage
    )

    answer = ""

    if "error" not in result:
        try:
            answer = explain_result(query, sql, result["rows"])
        except Exception as e:
            answer = f"Unable to generate explanation: {str(e)}"

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
                df = pd.DataFrame(rows, columns=columns)

                st.markdown("### 📊 Result")
                st.write(f"Rows: {len(df)}")
                st.dataframe(df)

            else:
                st.info("No data found")

    status = "success" if "error" not in result else "error"

    save_history(
        st.session_state.user["id"],
        st.session_state.user["email"],
        query,
        sql,
        answer,
        status
    )

    increment_query_count(st.session_state.user["id"])

    if st.session_state.user["role"] != "admin":
        st.session_state.user["query_count"] += 1