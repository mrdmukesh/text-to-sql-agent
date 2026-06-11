import streamlit as st

from services.insight_service import (
    get_table_names,
    load_table_as_df,
    generate_basic_insights
)


def render_insights():

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