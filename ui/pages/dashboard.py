import streamlit as st


def render_dashboard():

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