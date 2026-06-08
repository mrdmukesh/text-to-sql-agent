from backend.schema_loader import load_schema

def test_schema():
    schema = load_schema()

    # basic validation
    assert isinstance(schema, str)
    assert schema.strip() != ""

    # IMPORTANT: check key table exists
    assert "employees" in schema.lower()

def test_schema_contains_tables():
    schema = load_schema()
    assert "employees" in schema