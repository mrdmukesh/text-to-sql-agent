import os
import pandas as pd
import streamlit as st
from ui.pages.chunking_page import render_chunking_lab
from services.file_upload_service import (
    save_csv_to_sqlite,
    UPLOAD_DB
)

from services.history_service import (
    get_user_history,
    get_all_history,
    get_history_analytics
)

from services.auth_service import (
    get_all_users,
    update_user_status,
    get_user_analytics
)

from services.token_usage_service import (
    get_user_token_usage,
    get_all_token_usage
)


def render_sidebar():

    with st.sidebar:

        st.title("🧭 Control Panel")

        st.success(f"Logged in: {st.session_state.user['email']}")
        st.caption(f"Role: {st.session_state.user['role']}")

        if st.session_state.user["role"] != "admin":
            st.caption(
                f"Used Queries: "
                f"{st.session_state.user['query_count']}/"
                f"{st.session_state.user['query_limit']}"
            )

        token_stats = get_user_token_usage(st.session_state.user["id"])
        st.caption(f"Tokens Used: {token_stats['total_tokens']}")
        st.caption(f"Estimated Cost: ${token_stats['estimated_cost']}")

        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.chat = []
            st.rerun()

        st.markdown("---")

        selected_tool = st.radio(
            "🚀 Select Tool",
            
               [
                    "🏠 Dashboard",
                    "📊 Text-to-SQL",
                    "📈 AI Data Insights + Charts",
                    "🧩 RAG Chunking Strategy Lab",
                    "🤖 Enterprise RAG Assistant",
                    "🧾 Receipt Claim Assistant",
                    "🐯 Animal Face Transformer",
                    "🐦 Bird Voice Generator"
                ]
            
        )

        st.markdown("---")

        st.subheader("📂 Data Upload")

        uploaded_files = st.file_uploader(
            "Upload CSV files",
            type=["csv"],
            accept_multiple_files=True
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                try:
                    uploaded_file.seek(0)
                    table_name, columns = save_csv_to_sqlite(uploaded_file)

                    st.success(f"Uploaded: {uploaded_file.name}")
                    st.caption(f"Table: {table_name}")
                    st.write(columns)

                    uploaded_file.seek(0)
                    df_preview = pd.read_csv(uploaded_file)

                    with st.expander(f"Preview {uploaded_file.name}"):
                        st.dataframe(df_preview)

                except Exception as e:
                    st.error(f"Upload failed for {uploaded_file.name}: {str(e)}")

        st.markdown("---")

        with st.expander("🕘 My Recent Queries", expanded=False):
            history_rows = get_user_history(st.session_state.user["id"])

            if history_rows:
                for h in history_rows:
                    question, sql_query, answer, status, created_at = h
                    st.markdown(f"**{created_at}**")
                    st.write(question)
                    st.code(sql_query, language="sql")
                    st.caption(status)
                    st.markdown("---")
            else:
                st.info("No history yet.")

        if st.session_state.user["role"] == "admin":
            render_admin_panel()

        return selected_tool


def render_admin_panel():

    with st.expander("🛡️ Admin Panel", expanded=False):

        st.subheader("📊 Analytics")

        user_stats = get_user_analytics()
        history_stats = get_history_analytics()

        c1, c2 = st.columns(2)

        with c1:
            st.metric("Users", user_stats["total_users"])
            st.metric("Active", user_stats["active_users"])
            st.metric("Blocked", user_stats["blocked_users"])

        with c2:
            st.metric("Queries", history_stats["total_queries"])
            st.metric("Success", history_stats["successful_queries"])
            st.metric("Failed", history_stats["failed_queries"])

        st.markdown("---")
        st.markdown("### 💰 Token Usage Analytics")

        usage_rows = get_all_token_usage()

        if usage_rows:
            usage_df = pd.DataFrame(
                usage_rows,
                columns=[
                    "User Email",
                    "API Calls",
                    "Total Tokens",
                    "Estimated Cost ($)"
                ]
            )
            st.dataframe(usage_df)
        else:
            st.info("No token usage found yet.")

        st.markdown("---")
        st.markdown("### 🏆 Top Users")

        if history_stats["top_users"]:
            top_users_df = pd.DataFrame(
                history_stats["top_users"],
                columns=["User Email", "Query Count"]
            )
            st.dataframe(top_users_df)
        else:
            st.info("No query usage yet.")

        st.markdown("---")
        st.markdown("### 👥 User Management")

        users = get_all_users()

        for u in users:
            user_id, name, email, role, is_active, query_limit, query_count = u

            st.write(
                f"**{email}** | {role} | "
                f"Used: {query_count}/{query_limit}"
            )

            if role != "admin":
                if is_active:
                    if st.button(f"Block {email}", key=f"block_{user_id}"):
                        update_user_status(user_id, 0)
                        st.rerun()
                else:
                    if st.button(f"Activate {email}", key=f"activate_{user_id}"):
                        update_user_status(user_id, 1)
                        st.rerun()

        st.markdown("---")

        if st.button("🗑️ Clear Uploaded Data"):
            if os.path.exists(UPLOAD_DB):
                os.remove(UPLOAD_DB)
                st.success("Uploaded data cleared.")
                st.rerun()
            else:
                st.info("No uploaded data found.")

    with st.expander("📜 All Query History", expanded=False):
        all_history = get_all_history()

        if all_history:
            for h in all_history:
                user_email, question, sql_query, status, created_at = h
                st.markdown(f"**{created_at} | {user_email}**")
                st.write(question)
                st.code(sql_query, language="sql")
                st.caption(status)
                st.markdown("---")
        else:
            st.info("No query history found.")