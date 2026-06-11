from unittest.mock import patch, MagicMock
from backend.llm_engine import call_openai


def test_openai_response_mock():

    mock_response = MagicMock()
    mock_response.choices[0].message.content = "SELECT * FROM employees;"
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_response.usage.total_tokens = 15

    with patch("backend.llm_engine.client") as mock_client:
        mock_client.chat.completions.create.return_value = mock_response

        result, usage = call_openai(
            "show all employees",
            return_usage=True
        )

    assert result == "SELECT * FROM employees;"
    assert usage["total_tokens"] == 15