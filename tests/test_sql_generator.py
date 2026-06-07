from backend.sql_generator import generate_sql


def test_sql_generation_basic():

    question = "show all employees"

    sql = generate_sql(question)

    assert "SELECT" in sql.upper()
    assert "employees" in sql.lower()