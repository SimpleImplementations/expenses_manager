import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from src.llm_messages import CONTEXT

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ExpenseExtraction(BaseModel):
    value: float
    category: str
    currency: str


def llm_call(message: str) -> ExpenseExtraction:
    response = client.responses.parse(
        model="gpt-5-mini",
        input=[
            {"role": "system", "content": CONTEXT},
            {"role": "user", "content": message},
        ],
        text_format=ExpenseExtraction,
    )

    expense_extraction = response.output_parsed
    assert isinstance(expense_extraction, ExpenseExtraction)

    return expense_extraction


if __name__ == "__main__":
    messages = [
        "mc ayer",
        "ubi x laburo",
        "regalo cumple en USD",
        "cafe en la facu",
        "netflix mensual",
        "comida afuera mc",
    ]
    for message in messages:
        result = llm_call(message)
        print(f"Message: {message}\nResult: {result}\n")
