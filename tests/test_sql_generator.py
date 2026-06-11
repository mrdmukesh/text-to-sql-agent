from unittest.mock import patch
from backend.sql_generator import generate_sql


def test_sql_generation_basic():

    with patch("backend.sql_generator.call_openai") as mock_call:
        mock_call.return_value = (
            "SELECT * FROM employees;",
            {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        )

        sql, usage = generate_sql("show all employees")

    assert "SELECT" in sql.upper()
    assert usage["total_tokens"] == 15