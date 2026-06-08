"""
GenAI Studio Lab - AI Data Analyst with Login, Admin Control and Multi-CSV SQL
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
from services.history_service import save_history
from backend.schema_loader import load_schema
from services.file_upload_service import (
    save_csv_to_sqlite,
    get_uploaded_schema,
    UPLOAD_DB
)
from services.auth_service import (
    init_auth_db,
    register_user,
    login_user,
    get_or_create_google_user,
    can_run_query,
    increment_query_count,
    get_all_users,
    update_user_status
)


# ---------------- INIT ----------------
init_db()
init_auth_db()

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
    st.session_state.selected_tool = "Text-to-SQL"


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
        Login to access AI tools, data analysis and productivity features.
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
                user, msg = login_user(
                    login_email,
                    login_password
                )

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
# MAIN APP HEADER
# =========================================================
st.markdown(
    """
    <h1 style='text-align: center; color: #4A90E2;'>
    🧠 GenAI Studio Lab
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center;'>AI tools for data, automation and creativity.</p>",
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
            f"Usage: {st.session_state.user['query_count']}/"
            f"{st.session_state.user['query_limit']}"
        )

    if st.button("Logout"):
        st.session_state.user = None
        st.session_state.chat = []
        st.rerun()

    st.markdown("---")

    st.subheader("🧰 AI Tools")

    selected_tool = st.radio(
        "Choose a tool",
        [
            "Text-to-SQL",
            "Animal Face Transformer",
            "Bird Voice Generator"
        ]
    )

    st.session_state.selected_tool = selected_tool

    st.markdown("---")

    if st.session_state.user["role"] == "admin":

        with st.expander("🛡️ Admin Panel", expanded=False):

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


# =========================================================
# TOOL 1: TEXT TO SQL
# =========================================================
if st.session_state.selected_tool == "Text-to-SQL":

    st.subheader("📊 Text-to-SQL / Chat with Data")

    with st.sidebar:

        st.markdown("---")
        st.subheader("📂 Upload CSV Files")

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
                    st.write(f"Table: `{table_name}`")
                    st.write(columns)

                    uploaded_file.seek(0)
                    df_preview = pd.read_csv(uploaded_file)

                    with st.expander(f"Preview {uploaded_file.name}"):
                        st.dataframe(df_preview)

                except Exception as e:
                    st.error(
                        f"Upload failed for {uploaded_file.name}: {str(e)}"
                    )

        st.markdown("---")

        st.subheader("📌 Sample Queries")

        samples = [
            "show all employees",
            "Where does Mukesh Dabi live?",
            "Show Mukesh Dabi contact details",
            "Show all persons with their city",
            "Which person lives in Bangalore?"
        ]

        for q in samples:
            if st.button(q):
                st.session_state.pending_question = q
                st.rerun()

        st.markdown("---")

        st.subheader("📐 Database Schema")
        current_schema = load_schema() + "\n" + get_uploaded_schema()
        st.code(current_schema, language="text")

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

        sql = generate_sql(query)
        sql = sql.strip().replace("```sql", "").replace("```", "").strip()

        with st.chat_message("assistant"):
            st.markdown("### 🧠 Generated SQL")
            st.code(sql, language="sql")

        result = run_sql(sql)

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
                    df = pd.DataFrame(
                        rows,
                        columns=columns
                    )

                    st.markdown("### 📊 Result")
                    st.write(f"Rows: {len(df)}")
                    st.dataframe(df)

                else:
                    st.info("No data found")

        save_history(
            query,
            sql,
            result
        )

        increment_query_count(st.session_state.user["id"])

        if st.session_state.user["role"] != "admin":
            st.session_state.user["query_count"] += 1


# =========================================================
# TOOL 2: ANIMAL FACE TRANSFORMER
# =========================================================
elif st.session_state.selected_tool == "Animal Face Transformer":

    st.subheader("🐯 Animal Face Transformer")
    st.info("Coming soon.")

    st.markdown(
        """
        Future feature:
        - Upload face image
        - Select animal style
        - Generate transformed creative image
        """
    )


# =========================================================
# TOOL 3: BIRD VOICE GENERATOR
# =========================================================
elif st.session_state.selected_tool == "Bird Voice Generator":

    st.subheader("🐦 Bird Voice Generator")
    st.info("Coming soon.")

    st.markdown(
        """
        Future feature:
        - Type bird name
        - Generate or fetch bird sound
        - Play audio in browser
        """
    )