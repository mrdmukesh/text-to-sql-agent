from io import BytesIO
from unittest.mock import patch, MagicMock

from services.receipt_ai_service import extract_receipt_details


def test_extract_receipt_details_mocked():

    mock_response = MagicMock()
    mock_response.choices[0].message.content = """
    {
        "vendor_name": "VFS Global",
        "receipt_date": "2026-06-11",
        "amount": "3150",
        "currency": "USD",
        "tax_amount": "150",
        "category": "Visa",
        "payment_method": "CREDIT CARD",
        "invoice_number": "VISA-88271",
        "description": "Visa processing fee",
        "confidence_score": 0.95
    }
    """

    dummy_image = BytesIO(b"fake-image-content")
    dummy_image.name = "sample_visa_receipt.png"

    with patch("services.receipt_ai_service.get_openai_client") as mock_client_func:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_client_func.return_value = mock_client

        result = extract_receipt_details(dummy_image)

    assert result["vendor_name"] == "VFS Global"
    assert result["amount"] == "3150"
    assert result["currency"] == "USD"
    assert result["category"] == "Visa"