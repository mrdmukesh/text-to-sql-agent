from backend.schema_loader import load_schema


def test_schema():

    schema = load_schema()

    assert schema is not None
    assert len(schema) > 0