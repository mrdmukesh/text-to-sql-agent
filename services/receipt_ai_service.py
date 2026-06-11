import base64
import json
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_openai_client():
    api_key = None

    try:
        if "OPENAI_API_KEY" in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        api_key = None

    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found.")

    return OpenAI(api_key=api_key)


def encode_image(uploaded_file):
    uploaded_file.seek(0)
    image_bytes = uploaded_file.read()
    return base64.b64encode(image_bytes).decode("utf-8")


def extract_receipt_details(uploaded_file):
    client = get_openai_client()
    image_base64 = encode_image(uploaded_file)

    prompt = """
You are an AI receipt and reimbursement claim extraction assistant.

Extract details from the uploaded receipt image.

Return ONLY valid JSON with these fields:
{
  "vendor_name": "",
  "receipt_date": "",
  "amount": "",
  "currency": "",
  "tax_amount": "",
  "category": "",
  "payment_method": "",
  "invoice_number": "",
  "description": "",
  "confidence_score": ""
}

Rules:
- If a field is missing, use empty string.
- category should be one of: Visa, Travel, Food, Hotel, Transport, Office, Medical, Other.
- confidence_score should be a number between 0 and 1.
- Do not return markdown.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        },
                    },
                ],
            }
        ],
    )

    content = response.choices[0].message.content

    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }

    try:
        extracted_data = json.loads(content)
    except Exception:
        extracted_data = {
            "vendor_name": "",
            "receipt_date": "",
            "amount": "",
            "currency": "",
            "tax_amount": "",
            "category": "Other",
            "payment_method": "",
            "invoice_number": "",
            "description": content,
            "confidence_score": 0,
        }

    return extracted_data, usage