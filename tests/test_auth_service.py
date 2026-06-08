from services.auth_service import (
    init_auth_db,
    register_user,
    login_user,
    can_run_query,
    increment_query_count,
    get_all_users,
    update_user_status
)
import uuid

def test_register_and_login_user():

    init_auth_db()

    email = "test_user_auth@gmail.com"
    password = "Test@123"
    name = "Test User"

    register_user(name, email, password)

    user, msg = login_user(email, password)

    assert user is not None
    assert user["email"] == email
    assert user["role"] == "user"
    assert msg == "Login successful."


def test_admin_role_created():

    init_auth_db()

    email = "admin_test_unique@gmail.com"
    password = "Admin@123"
    name = "Mukesh Dabi"

    register_user(name, email, password)

    user, msg = login_user(email, password)

    assert user is not None
    assert user["role"] == "admin"


def test_query_limit_logic():

    user = {
        "id": 1,
        "role": "user",
        "query_limit": 10,
        "query_count": 5
    }

    assert can_run_query(user) is True

    user["query_count"] = 10

    assert can_run_query(user) is False


def test_admin_can_always_query():

    user = {
        "id": 1,
        "role": "admin",
        "query_limit": 0,
        "query_count": 999
    }

    assert can_run_query(user) is True


def test_block_user():

    init_auth_db()

    email = f"block_user_{uuid.uuid4().hex[:8]}@gmail.com"
    password = "Block@123"
    name = "Block User"

    register_user(name, email, password)

    user, msg = login_user(email, password)

    assert user is not None

    update_user_status(user["id"], 0)

    blocked_user, blocked_msg = login_user(email, password)

    assert blocked_user is None
    assert "blocked" in blocked_msg.lower()