import os
import pandas as pd
import streamlit as st

from services.file_upload_service import UPLOAD_DB

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
    user = st.session_state.get("user", {})
    role = user.get("role", "user")
    is_demo_user = role == "Demo Viewer"

    with st.sidebar:
        st.title("🧠 GenAI Studio")
        st.caption("AI Data Intelligence Platform")

        st.markdown("---")

        st.subheader("👤 User")
        st.success(user.get("email", "demo.user@portfolio.com"))
        st.caption(f"Role: {role}")

        if role == "admin":
            st.caption("Access: Unlimited Admin")
        elif is_demo_user:
            st.caption("Access: Portfolio Demo")
            st.caption("Used Queries: 0/5")
        else:
            st.caption(
                f"Used Queries: "
                f"{user.get('query_count', 0)}/"
                f"{user.get('query_limit', 5)}"
            )

        if is_demo_user:
            token_stats = {
                "total_tokens": 0,
                "estimated_cost": 0
            }
        else:
            try:
                token_stats = get_user_token_usage(user.get("id"))
            except Exception:
                token_stats = {
                    "total_tokens": 0,
                    "estimated_cost": 0
                }

        st.caption(f"Tokens Used: {token_stats.get('total_tokens', 0)}")
        st.caption(f"Estimated Cost: ${token_stats.get('estimated_cost', 0)}")

        if st.button("🚪 Logout", use_container_width=True):
            for key in [
                "user",
                "chat",
                "pending_question",
                "selected_tool",
                "demo_requests"
            ]:
                if key in st.session_state:
                    del st.session_state[key]

            st.rerun()

        st.markdown("---")

        selected_tool = st.radio(
            "🚀 Select Tool",
            [
                "🏠 Dashboard",
                "🏗️ Solution Architecture",
                "📊 Text-to-SQL",
                "📈 AI Data Insights + Charts",
                "☁️ Azure SQL Text-to-SQL",
                "🧩 RAG Chunking Strategy Lab",
                "🤖 Enterprise RAG Assistant",
                "🧾 Receipt Claim Assistant",
                "🐯 Animal Face Transformer",
                "🐦 Bird Voice Generator"
            ]
        )

        st.markdown("---")

        with st.expander("🕘 My Recent Queries", expanded=False):
            if is_demo_user:
                st.info("Query history is disabled in portfolio demo mode.")
            else:
                try:
                    history_rows = get_user_history(user.get("id"))

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

                except Exception as e:
                    st.warning(f"Unable to load query history: {str(e)}")

        if role == "admin":
            render_admin_panel()

        return selected_tool


def render_admin_panel():
    with st.expander("🛡️ Admin Panel", expanded=False):
        st.subheader("📊 Platform Analytics")

        user_stats = get_user_analytics()
        history_stats = get_history_analytics()

        c1, c2 = st.columns(2)

        with c1:
            st.metric("Users", user_stats.get("total_users", 0))
            st.metric("Active", user_stats.get("active_users", 0))
            st.metric("Blocked", user_stats.get("blocked_users", 0))

        with c2:
            st.metric("Queries", history_stats.get("total_queries", 0))
            st.metric("Success", history_stats.get("successful_queries", 0))
            st.metric("Failed", history_stats.get("failed_queries", 0))

        st.markdown("---")
        st.markdown("### 💰 Token Usage")

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
            st.dataframe(usage_df, use_container_width=True)
        else:
            st.info("No token usage found yet.")

        st.markdown("---")
        st.markdown("### 🏆 Top Users")

        if history_stats.get("top_users"):
            top_users_df = pd.DataFrame(
                history_stats["top_users"],
                columns=["User Email", "Query Count"]
            )
            st.dataframe(top_users_df, use_container_width=True)
        else:
            st.info("No query usage yet.")

        st.markdown("---")
        st.markdown("### 👥 User Management")

        users = get_all_users()

        for u in users:
            user_id = u[0]
            email = u[2]
            role = u[3]
            is_active = u[4]
            query_limit = u[5]
            query_count = u[6]

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

        if st.button("🗑️ Clear Uploaded Data", use_container_width=True):
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