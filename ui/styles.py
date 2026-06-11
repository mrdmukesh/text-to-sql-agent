import streamlit as st


def apply_styles():
    st.markdown("""
    <style>
    .hero-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 45%, #2563eb 100%);
        padding: 42px;
        border-radius: 24px;
        color: white;
        box-shadow: 0 20px 45px rgba(0,0,0,0.25);
    }

    .hero-title {
        font-size: 44px;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .hero-subtitle {
        font-size: 18px;
        color: #dbeafe;
        margin-bottom: 20px;
    }

    .footer-text {
        text-align: center;
        color: #94a3b8;
        font-size: 13px;
        margin-top: 35px;
    }
    </style>
    """, unsafe_allow_html=True)