import sqlite3
import pandas as pd
from services.file_upload_service import UPLOAD_DB


def get_table_names():
    conn = sqlite3.connect(UPLOAD_DB)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    conn.close()
    return tables


def load_table_as_df(table_name):
    conn = sqlite3.connect(UPLOAD_DB)

    df = pd.read_sql_query(
        f"SELECT * FROM {table_name}",
        conn
    )

    conn.close()
    return df


def generate_basic_insights(df):
    insights = {}

    insights["row_count"] = len(df)
    insights["column_count"] = len(df.columns)
    insights["columns"] = list(df.columns)

    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    categorical_columns = df.select_dtypes(exclude="number").columns.tolist()

    insights["numeric_columns"] = numeric_columns
    insights["categorical_columns"] = categorical_columns
    insights["missing_values"] = df.isnull().sum().to_dict()

    if numeric_columns:
        insights["numeric_summary"] = df[numeric_columns].describe().to_dict()

    return insights


def get_category_count(df, column):
    return df[column].value_counts().reset_index().rename(
        columns={
            "index": column,
            column: "count"
        }
    )