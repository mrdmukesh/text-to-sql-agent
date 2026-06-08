from data.database import init_db
from backend.schema_loader import load_schema


def test_schema():

    init_db()

    schema = load_schema()

    assert isinstance(schema, str)
    assert schema.strip() != ""


def test_schema_contains_tables():

    init_db()

    schema = load_schema()

    assert "employees" in schema.lower()