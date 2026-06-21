from pathlib import Path
import streamlit as st

def render_architecture_page():

    st.title("🏗️ GenAI Studio Lab - Solution Architecture")

    image_path = Path.cwd() / "app" / "assets" / "arch.png"

    

    if image_path.exists():
        col1, col2, col3 = st.columns([1, 8, 1])

        with col2:
            st.image(
                str(image_path),
                caption="GenAI Studio Lab - End-to-End Technical Architecture"
            )
    else:
        st.error(f"Image not found: {image_path}")