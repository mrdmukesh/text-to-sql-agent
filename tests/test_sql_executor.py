from backend.sql_executor import run_sql


def test_sql_execution():

    sql = "SELECT 1"

    result = run_sql(sql)

    assert "rows" in result
    assert "columns" in result