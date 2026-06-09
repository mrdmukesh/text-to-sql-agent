"""
GenAI Studio Lab - Professional Multi-Tool AI Platform
"""

import sys
import os
import requests
import streamlit as st
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from streamlit_oauth import OAuth2Component

from backend.sql_generator import generate_sql
from backend.sql_executor import run_sql
from backend.result_explainer import explain_result
from data.database import init_db
from backend.schema_loader import load_schema

from services.file_upload_service import (
    save_csv_to_sqlite,
    get_uploaded_schema,
    UPLOAD_DB
)

from services.insight_service import (
    get_table_names,
    load_table_as_df,
    generate_basic_insights
)

from services.history_service import (
    init_history_db,
    save_history,
    get_user_history,
    get_all_history,
    get_history_analytics
)

from services.auth_service import (
    init_auth_db,
    register_user,
    login_user,
    get_or_create_google_user,
    can_run_query,
    increment_query_count,
    get_all_users,
    update_user_status,
    get_user_analytics
)
from services.token_usage_service import (
    init_usage_db,
    save_token_usage,
    get_user_token_usage,
    get_all_token_usage
)

# ---------------- INIT ----------------
init_db()
init_auth_db()
init_history_db()
init_usage_db()

st.set_page_config(
    page_title="GenAI Studio Lab",
    page_icon="🧠",
    layout="wide"
)


# ---------------- GOOGLE OAUTH CONFIG ----------------
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REFRESH_TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_TOKEN_URL = "https://oauth2.googleapis.com/revoke"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

oauth2 = OAuth2Component(
    st.secrets["GOOGLE_CLIENT_ID"],
    st.secrets["GOOGLE_CLIENT_SECRET"],
    AUTHORIZE_URL,
    TOKEN_URL,
    REFRESH_TOKEN_URL,
    REVOKE_TOKEN_URL
)


# ---------------- SESSION STATE ----------------
if "chat" not in st.session_state:
    st.session_state.chat = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

if "user" not in st.session_state:
    st.session_state.user = None

if "selected_tool" not in st.session_state:
    st.session_state.selected_tool = "🏠 Dashboard"


# =========================================================
# LOGIN / REGISTER PAGE
# =========================================================
if st.session_state.user is None:

    st.markdown(
        """
        <h1 style='text-align: center; color: #4A90E2;'>
        🧠 GenAI Studio Lab
        </h1>
        <p style='text-align: center; font-size: 18px;'>
        Secure AI tools for data analysis, automation and creativity.
        </p>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])

        with tab_login:

            st.markdown("### Continue with Google")

            result = oauth2.authorize_button(
                name="Login with Google",
                redirect_uri=st.secrets["REDIRECT_URI"],
                scope="openid email profile",
                key="google_login"
            )

            if result and "token" in result:
                token = result["token"]

                headers = {
                    "Authorization": f"Bearer {token['access_token']}"
                }

                user_info = requests.get(
                    USER_INFO_URL,
                    headers=headers,
                    timeout=10
                ).json()

                google_name = user_info.get("name", "")
                google_email = user_info.get("email", "")

                if google_email:
                    user, msg = get_or_create_google_user(
                        google_name,
                        google_email
                    )

                    if user:
                        st.session_state.user = user
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Unable to get email from Google.")

            st.markdown("---")
            st.markdown("### Or login with email/password")

            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input(
                "Password",
                type="password",
                key="login_password"
            )

            if st.button("Login", use_container_width=True):
                user, msg = login_user(login_email, login_password)

                if user:
                    st.session_state.user = user
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        with tab_register:

            reg_name = st.text_input("Name", key="reg_name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input(
                "Password",
                type="password",
                key="reg_password"
            )

            if st.button("Register", use_container_width=True):
                if not reg_name or not reg_email or not reg_password:
                    st.error("Please enter name, email and password.")
                else:
                    success, msg = register_user(
                        reg_name,
                        reg_email,
                        reg_password
                    )

                    if success:
                        st.success(msg)
                        st.info("Please go to Login tab and login.")
                    else:
                        st.error(msg)

    st.stop()


# =========================================================
# APP HEADER
# =========================================================
st.markdown(
    """
    <h1 style='text-align: center; color: #4A90E2;'>
    🧠 GenAI Studio Lab
    </h1>
    <p style='text-align: center; font-size: 16px;'>
    AI-powered data analysis, SQL intelligence and future creative tools.
    </p>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================
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
    token_stats = get_user_token_usage(
    st.session_state.user["id"]
    )

    st.caption(
        f"Tokens Used: {token_stats['total_tokens']}"
    )

    st.caption(
        f"Estimated Cost: ${token_stats['estimated_cost']}"
    )
    if st.session_state.user["role"] != "admin":
        st.caption(
            f"Usage: {st.session_state.user['query_count']}/"
            f"{st.session_state.user['query_limit']}"
        )

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
            "🐯 Animal Face Transformer",
            "🐦 Bird Voice Generator"
        ]
    )

    st.session_state.selected_tool = selected_tool

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

        with st.expander("🛡️ Admin Panel", expanded=False):

            st.subheader("📊 Analytics")
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
                        if st.button(
                            f"Block {email}",
                            key=f"block_{user_id}"
                        ):
                            update_user_status(user_id, 0)
                            st.rerun()
                    else:
                        if st.button(
                            f"Activate {email}",
                            key=f"activate_{user_id}"
                        ):
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


# =========================================================
# DASHBOARD
# =========================================================
if st.session_state.selected_tool == "🏠 Dashboard":

    st.subheader("🏠 Platform Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Active Tool", "Text-to-SQL")
        st.info("Ask questions in natural language and get SQL results.")

    with col2:
        st.metric("Data Insights", "Available")
        st.info("Analyze uploaded CSV files and generate charts.")

    with col3:
        st.metric("Creative Tools", "Coming Soon")
        st.info("Animal face and bird voice tools are planned.")

    st.markdown("---")

    st.markdown("### Available Tools")

    t1, t2, t3 = st.columns(3)

    with t1:
        st.markdown("#### 📊 Text-to-SQL")
        st.write("Query default or uploaded relational CSV data.")
        if st.button("Open Text-to-SQL"):
            st.session_state.selected_tool = "📊 Text-to-SQL"
            st.rerun()

    with t2:
        st.markdown("#### 📈 AI Data Insights + Charts")
        st.write("Generate summaries and charts from uploaded CSV files.")
        if st.button("Open Insights"):
            st.session_state.selected_tool = "📈 AI Data Insights + Charts"
            st.rerun()

    with t3:
        st.markdown("#### 🧪 Future Tools")
        st.write("Animal Face Transformer and Bird Voice Generator.")


# =========================================================
# TEXT TO SQL
# =========================================================
elif st.session_state.selected_tool == "📊 Text-to-SQL":

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
                answer = explain_result(
                    query,
                    sql,
                    result["rows"]
                )
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


# =========================================================
# AI DATA INSIGHTS + CHARTS
# =========================================================
elif st.session_state.selected_tool == "📈 AI Data Insights + Charts":

    st.subheader("📈 AI Data Insights + Charts")

    tables = get_table_names()

    if not tables:
        st.warning("Please upload one or more CSV files from the sidebar first.")
        st.stop()

    selected_table = st.selectbox(
        "Select uploaded table",
        tables
    )

    df = load_table_as_df(selected_table)

    st.markdown("### Data Preview")
    st.dataframe(df.head())

    insights = generate_basic_insights(df)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Rows", insights["row_count"])

    with c2:
        st.metric("Columns", insights["column_count"])

    with c3:
        st.metric("Missing Values", sum(insights["missing_values"].values()))

    tab_summary, tab_chart = st.tabs(["📋 Summary", "📊 Charts"])

    with tab_summary:
        st.markdown("### Columns")
        st.write(insights["columns"])

        st.markdown("### Numeric Columns")
        st.write(insights["numeric_columns"])

        st.markdown("### Categorical Columns")
        st.write(insights["categorical_columns"])

        st.markdown("### Missing Values")
        st.write(insights["missing_values"])

        if insights["numeric_columns"]:
            st.markdown("### Numeric Summary")
            st.dataframe(df[insights["numeric_columns"]].describe())

    with tab_chart:
        if insights["categorical_columns"]:
            chart_column = st.selectbox(
                "Select categorical column",
                insights["categorical_columns"]
            )

            chart_data = df[chart_column].value_counts()

            st.markdown(f"### Count by {chart_column}")
            st.bar_chart(chart_data)
        else:
            st.info("No categorical column available for chart.")


# =========================================================
# ANIMAL FACE TRANSFORMER
# =========================================================
elif st.session_state.selected_tool == "🐯 Animal Face Transformer":

    st.subheader("🐯 Animal Face Transformer")
    st.info("Coming soon.")

    st.markdown(
        """
        Planned feature:
        - Upload face image
        - Select animal style
        - Generate transformed creative image
        """
    )


# =========================================================
# BIRD VOICE GENERATOR
# =========================================================
elif st.session_state.selected_tool == "🐦 Bird Voice Generator":

    st.subheader("🐦 Bird Voice Generator")
    st.info("Coming soon.")

    st.markdown(
        """
        Planned feature:
        - Type bird name
        - Generate or fetch bird sound
        - Play audio in browser
        """
    )