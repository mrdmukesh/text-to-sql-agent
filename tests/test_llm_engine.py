from backend.llm_engine import call_openai


#def test_openai_response():

 #   result = call_openai("Return SQL: show employees")

   # assert result is not None
    #assert len(result) > 0


def mock_llm(prompt):
    return "SELECT * FROM employees"

def test_openai_response_mock(monkeypatch):

    # Fake response function
    def mock_openai(prompt):
        return "SELECT * FROM employees"

    # Replace real API call with mock
    monkeypatch.setattr(
        "backend.llm_engine.call_openai",
        mock_openai
    )

    result = call_openai("show employees")

    assert "SELECT" in result
    assert "employees" in result