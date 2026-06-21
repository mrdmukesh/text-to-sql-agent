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


def unique_email(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@gmail.com"


def test_register_and_login_user():
    init_auth_db()

    email = unique_email("test_user_auth")
    password = "Test@123"
    name = "Test User"

    success, msg = register_user(name, email, password)
    assert success is True

    user, msg = login_user(email, password)

    assert user is not None
    assert user["email"] == email
    assert user["role"] == "user"
    assert user["query_limit"] == 5
    assert user["query_count"] == 0
    assert user["is_unlocked"] is False
    assert user["plan"] == "free"
    assert msg == "Login successful."


def test_admin_role_created_and_unlimited():
    init_auth_db()

    email = "admin_test_unique@gmail.com"
    password = "Admin@123"
    name = "Mukesh Dabi"

    register_user(name, email, password)

    user, msg = login_user(email, password)

    assert user is not None
    assert user["role"] == "admin"
    assert can_run_query(user) is True


def test_free_user_can_query_within_limit():
    user = {
        "id": 1,
        "role": "user",
        "query_limit": 5,
        "query_count": 4,
        "is_unlocked": False
    }

    assert can_run_query(user) is True


def test_free_user_blocked_after_limit():
    user = {
        "id": 1,
        "role": "user",
        "query_limit": 5,
        "query_count": 5,
        "is_unlocked": False
    }

    assert can_run_query(user) is False


def test_admin_can_always_query():
    user = {
        "id": 1,
        "role": "admin",
        "query_limit": 0,
        "query_count": 999,
        "is_unlocked": False
    }

    assert can_run_query(user) is True


def test_unlocked_user_can_query_after_limit():
    user = {
        "id": 1,
        "role": "user",
        "query_limit": 5,
        "query_count": 100,
        "is_unlocked": True
    }

    assert can_run_query(user) is True


def test_block_user():
    init_auth_db()

    email = unique_email("block_user")
    password = "Block@123"
    name = "Block User"

    success, msg = register_user(name, email, password)
    assert success is True

    user, msg = login_user(email, password)

    assert user is not None

    update_user_status(user["id"], 0)

    blocked_user, blocked_msg = login_user(email, password)

    assert blocked_user is None
    assert "blocked" in blocked_msg.lower()


def test_increment_query_count():
    init_auth_db()

    email = unique_email("usage_user")
    password = "Usage@123"
    name = "Usage User"

    success, msg = register_user(name, email, password)
    assert success is True

    user, msg = login_user(email, password)

    assert user["query_count"] == 0

    increment_query_count(user["id"])

    updated_user, msg = login_user(email, password)

    assert updated_user["query_count"] == 1