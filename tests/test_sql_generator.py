from backend.sql_generator import generate_sql


def test_sql_generation_basic():

    question = "show all employees"

    sql, usage = generate_sql(question)

    assert "SELECT" in sql.upper()
    assert isinstance(usage, dict)
    assert "employees" in sql.lower()