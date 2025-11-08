import os
from typing import List, Literal, cast

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, create_model

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ExpenseExtraction(BaseModel):
    value: float
    category: str
    currency: str


def make_expense_model(categories: list[str]) -> type[BaseModel]:
    Cat = Literal[tuple(categories)]  # type: ignore # dynamic Literal

    return create_model(
        "ExpenseExtraction",
        value=(float, Field(description="Monto numérico", default=0.0)),
        category=(Cat, Field(description="Categoría del gasto")),
        currency=(str, Field(description="Moneda ISO", default="ARS")),
        __base__=BaseModel,
    )


def create_context(categories: List[str]) -> str:
    return f"""El mensaje describe un gasto de dinero personal de un usuario enviado por un corto mensaje de texto.
    Extrae:
    - valor: monto numérico del gasto (usar punto como separador decimal).
    - categoría: la categoría del gasto. Las opciones son: {", ".join(categories)}.
    - moneda: la moneda del gasto (por defecto ARS si no se menciona).
    Si no hay buena coincidencia con las categorías, usar "Otros".
    Si no hay valor, asignar 0.0.
    """


def llm_call(message: str, categories: List[str]) -> ExpenseExtraction:
    RuntimeModel = make_expense_model(categories)
    context = create_context(categories)
    response = client.responses.parse(
        model="gpt-4.1-mini",  # "gpt-5-mini",
        input=[
            {"role": "system", "content": context},
            {"role": "user", "content": message},
        ],
        text_format=RuntimeModel,
    )

    expense_extraction = response.output_parsed
    assert isinstance(expense_extraction, RuntimeModel)

    parsed = ExpenseExtraction(**expense_extraction.model_dump())
    return cast(ExpenseExtraction, parsed)


if __name__ == "__main__":

    from src.base_categories import BASE_CATEGORIES

    messages = [
        "mc ayer",
        "ubi x laburo",
        "regalo cumple en USD",
        "cafe en la facu",
        "netflix mensual",
        "comida afuera mc",
    ]
    for message in messages:
        result = llm_call(message, BASE_CATEGORIES)  # type: ignore
        print(f"Message: {message}\nResult: {result}\n")
