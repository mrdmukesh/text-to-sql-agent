from services.history_service import (
    init_history_db,
    save_history,
    get_user_history,
    get_all_history
)


def test_save_and_get_user_history():

    init_history_db()

    save_history(
        user_id=1,
        user_email="test@gmail.com",
        question="show all employees",
        sql_query="SELECT * FROM employees",
        answer="Employees displayed",
        status="success"
    )

    rows = get_user_history(1)

    assert len(rows) > 0

    question, sql_query, answer, status, created_at = rows[0]

    assert "show all employees" == question
    assert "SELECT" in sql_query
    assert status == "success"


def test_get_all_history():

    init_history_db()

    rows = get_all_history()

    assert isinstance(rows, list)
