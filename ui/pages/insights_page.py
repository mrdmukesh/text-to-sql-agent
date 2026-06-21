import pandas as pd
import streamlit as st

from services.file_upload_service import save_csv_to_sqlite
from services.insight_service import (
    get_table_names,
    load_table_as_df,
    generate_basic_insights
)


def render_insights():
    st.subheader("📈 AI Data Insights + Charts")

    st.info(
        "Upload a CSV file to generate data preview, summary statistics, "
        "missing value analysis and basic charts."
    )

    # =========================
    # CSV UPLOAD SECTION
    # =========================
    uploaded_file = st.file_uploader(
        "📂 Upload CSV file for analysis",
        type=["csv"],
        key="insights_csv_upload"
    )

    if uploaded_file:
        try:
            uploaded_file.seek(0)
            table_name, columns = save_csv_to_sqlite(uploaded_file)

            st.success(f"Uploaded successfully as table: {table_name}")
            st.caption("Detected columns:")
            st.write(columns)

            uploaded_file.seek(0)
            preview_df = pd.read_csv(uploaded_file)

            with st.expander("Preview uploaded file", expanded=True):
                st.dataframe(preview_df.head(), use_container_width=True)

        except Exception as e:
            st.error(f"Upload failed: {str(e)}")
            st.stop()

    # =========================
    # LOAD AVAILABLE TABLES
    # =========================
    tables = get_table_names()

    if not tables:
        st.warning("Please upload a CSV file to continue.")
        st.stop()

    selected_table = st.selectbox(
        "Select table for analysis",
        tables,
        key="insights_selected_table"
    )

    df = load_table_as_df(selected_table)

    if df.empty:
        st.warning("Selected table has no data.")
        st.stop()

    # =========================
    # DATA PREVIEW
    # =========================
    st.markdown("### Data Preview")
    st.dataframe(df.head(), use_container_width=True)

    insights = generate_basic_insights(df)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Rows", insights["row_count"])

    with c2:
        st.metric("Columns", insights["column_count"])

    with c3:
        st.metric("Missing Values", sum(insights["missing_values"].values()))

    # =========================
    # SUMMARY + CHARTS
    # =========================
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
            st.dataframe(
                df[insights["numeric_columns"]].describe(),
                use_container_width=True
            )

    with tab_chart:
        if insights["categorical_columns"]:
            chart_column = st.selectbox(
                "Select categorical column",
                insights["categorical_columns"],
                key="insights_chart_column"
            )

            chart_data = df[chart_column].value_counts()

            st.markdown(f"### Count by {chart_column}")
            st.bar_chart(chart_data)
        else:
            st.info("No categorical column available for chart.")