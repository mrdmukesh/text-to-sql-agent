import streamlit as st


def render_coming_soon(title, features):

    st.subheader(title)
    st.info("Coming soon.")

    st.markdown("### Planned Features")

    for feature in features:
        st.write(f"- {feature}")