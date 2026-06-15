import streamlit as st

from services.azure_sql_service import (
    get_azure_sql_schema,
    generate_azure_sql,
    execute_azure_sql
)


def render_azure_sql_text_to_sql():
    st.subheader("☁️ Azure SQL Text-to-SQL")

    st.markdown(
        """
        Ask natural language questions on the enterprise Supply Chain Operations Azure SQL database.
        """
    )

    with st.expander("View Azure SQL Schema"):
        try:
            schema = get_azure_sql_schema()
            st.code(schema, language="text")
        except Exception as e:
            st.error("Unable to load Azure SQL schema.")
            st.exception(e)

    question = st.text_area(
        "Ask a business question",
        placeholder="Example: Show delayed shipments by customer"
    )

    if st.button("Generate and Run Azure SQL Query"):
        if not question.strip():
            st.warning("Please enter a question.")
            return

        try:
            with st.spinner("Generating SQL using GenAI..."):
                sql = generate_azure_sql(question)

            st.markdown("### Generated SQL")
            st.code(sql, language="sql")

            with st.spinner("Executing query on Azure SQL..."):
                result_df = execute_azure_sql(sql)

            st.markdown("### Result")
            st.dataframe(result_df, use_container_width=True)

        except Exception as e:
            st.error("Azure SQL Text-to-SQL failed.")
            st.exception(e)