import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()


def get_config_value(key):
    value = os.getenv(key)

    if value:
        return value

    try:
        return st.secrets[key]
    except Exception:
        return None


api_key = get_config_value("OPENAI_API_KEY")

client = None

if api_key:
    client = OpenAI(api_key=api_key)


@traceable(name="OpenAI LLM Call")
def call_openai(prompt: str, return_usage: bool = False):

    if client is None:
        raise ValueError(
            "OPENAI_API_KEY is missing. Please set it in .env, Azure Key Vault, or Streamlit secrets."
        )

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

    result = response.choices[0].message.content

    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }

    if return_usage:
        return result, usage

    return result