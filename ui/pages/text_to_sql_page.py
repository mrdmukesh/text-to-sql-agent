import pandas as pd
import streamlit as st

from backend.sql_generator import generate_sql
from backend.sql_executor import run_sql
from backend.result_explainer import explain_result
from backend.schema_loader import load_schema

from services.file_upload_service import (
    save_csv_to_sqlite,
    get_uploaded_schema
)

from services.auth_service import can_run_query, increment_query_count
from services.history_service import save_history
from services.token_usage_service import save_token_usage


def render_text_to_sql():
    st.subheader("📊 Text-to-SQL / Chat with Data")

    st.info(
        "Upload one or more CSV files, review the generated schema, "
        "and ask natural-language questions. The app will generate SQL and return results."
    )

    # =========================
    # CSV UPLOAD SECTION
    # =========================
    uploaded_files = st.file_uploader(
        "📂 Upload one or more CSV files",
        type=["csv"],
        accept_multiple_files=True,
        key="text_to_sql_upload"
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                uploaded_file.seek(0)
                table_name, columns = save_csv_to_sqlite(uploaded_file)

                st.success(f"Uploaded successfully: {uploaded_file.name}")
                st.caption(f"Created table: {table_name}")
                st.write("Detected columns:")
                st.write(columns)

                uploaded_file.seek(0)
                preview_df = pd.read_csv(uploaded_file)

                with st.expander(f"Preview {uploaded_file.name}", expanded=False):
                    st.dataframe(preview_df.head(), use_container_width=True)

            except Exception as e:
                st.error(f"Upload failed for {uploaded_file.name}: {str(e)}")

    # =========================
    # SCHEMA VIEW
    # =========================
    with st.expander("📐 Current Database Schema", expanded=False):
        current_schema = load_schema() + "\n" + get_uploaded_schema()
        st.code(current_schema, language="text")

    # =========================
    # SAMPLE QUESTIONS
    # =========================
    st.markdown("### Suggested Questions")

    samples = [
        "Show all employees",
        "Show top 10 records",
        "Count records by city",
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

    # =========================
    # CHAT HISTORY
    # =========================
    if "chat" not in st.session_state:
        st.session_state.chat = []

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
    user = st.session_state.user
    is_admin = user.get("role") == "admin"

    if not can_run_query(user):
        st.error(
            "Your free demo query limit has been reached. "
            "Please contact Mukesh Dabi to unlock additional access."
        )
        st.stop()

    st.session_state.chat.append({
        "role": "user",
        "content": query
    })

    with st.chat_message("user"):
        st.write(query)

    try:
        sql, usage = generate_sql(query)
        sql = sql.strip().replace("```sql", "").replace("```", "").strip()

    except Exception as e:
        st.error(f"Unable to generate SQL: {str(e)}")
        return

    with st.chat_message("assistant"):
        st.markdown("### 🧠 Generated SQL")
        st.code(sql, language="sql")

    try:
        result = run_sql(sql)
    except Exception as e:
        result = {
            "error": f"SQL execution failed: {str(e)}"
        }

    # Save token usage only if available
    try:
        save_token_usage(
            user["id"],
            user["email"],
            "Text-to-SQL",
            usage
        )
    except Exception:
        pass

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
            rows = result.get("rows", [])
            columns = result.get("columns", [])

            if rows:
                df = pd.DataFrame(rows, columns=columns)

                st.markdown("### 📊 Result")
                st.write(f"Rows: {len(df)}")
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No data found.")

    status = "success" if "error" not in result else "error"

    try:
        save_history(
            user["id"],
            user["email"],
            query,
            sql,
            answer,
            status
        )
    except Exception:
        pass

    # Admin should have no limit
    if not is_admin:
        try:
            increment_query_count(user["id"])
            st.session_state.user["query_count"] = (
                st.session_state.user.get("query_count", 0) + 1
            )
        except Exception:
            pass