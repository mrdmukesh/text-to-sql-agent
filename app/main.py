import sys
import os

import streamlit as st
from streamlit_oauth import OAuth2Component

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data.database import init_db
from ui.pages.animal_transform_page import render_animal_transform
from services.auth_service import init_auth_db
from services.history_service import init_history_db
from services.token_usage_service import init_usage_db
from services.claim_service import init_claim_db

from ui.styles import apply_styles
from ui.auth_page import render_login_page
from ui.sidebar import render_sidebar

from ui.pages.dashboard import render_dashboard
from ui.pages.text_to_sql_page import render_text_to_sql
from ui.pages.insights_page import render_insights
from ui.pages.receipt_claim_page import render_receipt_claim
from ui.pages.chunking_page import render_chunking_lab
from ui.pages.coming_soon import render_coming_soon
from ui.pages.rag_assistant_page import render_rag_assistant

# =========================================================
# INIT
# =========================================================
init_db()
init_auth_db()
init_history_db()
init_usage_db()
init_claim_db()

st.set_page_config(
    page_title="GenAI Studio Lab",
    page_icon="🧠",
    layout="wide"
)

apply_styles()


# =========================================================
# GOOGLE OAUTH CONFIG
# =========================================================
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


# =========================================================
# SESSION STATE
# =========================================================
if "chat" not in st.session_state:
    st.session_state.chat = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

if "user" not in st.session_state:
    st.session_state.user = None

if "selected_tool" not in st.session_state:
    st.session_state.selected_tool = "🏠 Dashboard"


# =========================================================
# LOGIN PAGE
# =========================================================
if st.session_state.user is None:
    render_login_page(oauth2, USER_INFO_URL)
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
    AI-powered data analysis, SQL intelligence and business automation.
    </p>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================
selected_tool = render_sidebar()
st.session_state.selected_tool = selected_tool


# =========================================================
# ROUTER
# =========================================================
if selected_tool == "🏠 Dashboard":
    render_dashboard()

elif selected_tool == "📊 Text-to-SQL":
    render_text_to_sql()

elif selected_tool == "📈 AI Data Insights + Charts":
    render_insights()

elif selected_tool == "🧩 RAG Chunking Strategy Lab":
    render_chunking_lab()

elif selected_tool == "🤖 Enterprise RAG Assistant":
    render_rag_assistant()

elif selected_tool == "🧾 Receipt Claim Assistant":
    render_receipt_claim()

elif selected_tool == "🐯 Animal Face Transformer":
    render_animal_transform()

elif selected_tool == "🐦 Bird Voice Generator":
    render_coming_soon(
        "🐦 Bird Voice Generator",
        [
            "Type bird name",
            "Generate or fetch bird sound",
            "Play audio in browser"
        ]
    )