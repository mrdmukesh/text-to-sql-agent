import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = None

try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found."
    )

client = OpenAI(api_key=api_key)


def call_openai(prompt: str):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert SQL generator."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content