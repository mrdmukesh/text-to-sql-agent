from backend.llm_engine import call_openai
from backend.schema_loader import load_schema
from models.prompts import SQL_PROMPT


def generate_sql(question: str):

    schema = load_schema()

    prompt = SQL_PROMPT.format(
        schema=schema,
        question=question
    )

    #print("\n===== PROMPT SENT TO GPT =====")
    #print(prompt)
    #print("=============================\n")

    return call_openai(prompt)