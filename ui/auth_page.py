import os

import requests
import streamlit as st

from services.auth_service import (
    register_user,
    login_user,
    get_or_create_google_user
)


def render_login_page(oauth2, user_info_url):

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown(
            """
            <div class="hero-card">
                <div class="hero-title">🧠 GenAI Studio Lab</div>
                <div class="hero-subtitle">
                    Enterprise-style GenAI platform for data intelligence,
                    document processing and business automation.
                </div>
                <b>Built for secure AI productivity.</b>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### Platform Capabilities")
        st.info("📊 Text-to-SQL over default and uploaded relational CSV data")
        st.info("📈 AI data insights, summaries and charts from CSV files")
        st.info("🧾 Receipt claim extraction using multimodal AI")
        st.info("🧩 RAG chunking strategy lab for document retrieval simulation")
        st.info("🔐 Google OAuth login with role-based access control")
        st.info("💰 Token usage monitoring and admin analytics")
        st.info("🛡️ Admin control for users, limits, claims and governance")

    with right:
        st.markdown("## Welcome back")
        st.caption("Sign in to continue to your AI workspace.")

        tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])

        with tab_login:
            st.markdown("#### Continue with Google")

            result = oauth2.authorize_button(
                name="Login with Google",
                redirect_uri=os.getenv("REDIRECT_URI") or st.secrets.get("REDIRECT_URI"),
                scope="openid email profile",
                key="google_login"
            )

            if result and "token" in result:
                token = result["token"]

                headers = {
                    "Authorization": f"Bearer {token['access_token']}"
                }

                user_info = requests.get(
                    user_info_url,
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
            st.markdown("#### Or use email/password")

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
            st.markdown("#### Create account")

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

    st.markdown(
        """
        <div class="footer-text">
        © 2026 GenAI Studio Lab. Built by Mukesh Dabi. All rights reserved.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

with st.expander("🔒 Privacy & Data Usage"):

    st.markdown("""
    ### Privacy Notice

    This application uses AI services to provide features such as:
    - Text-to-SQL generation
    - Receipt claim extraction
    - RAG chunking simulation

    #### Data Handling
    - Uploaded files and questions are processed only for application functionality.
    - Some AI-powered features send prompts or uploaded content to OpenAI API for processing.
    - Uploaded data is not publicly shared with other users.
    - User history, token usage, and claims are isolated per user account.

    #### Admin Visibility
    - Application administrators may access analytics, token usage, and submitted claims for support and governance purposes.

    #### Storage
    - Data is currently stored in SQLite databases used by the application:
        - auth.db
        - history.db
        - usage.db
        - claims.db

    #### Recommendation
    Please avoid uploading:
    - passwords
    - confidential company secrets
    - highly sensitive personal information

    By using this application, you acknowledge and accept this data usage behavior.
    """)