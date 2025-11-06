import pytest

from src.parse_expenses_message import parse_expenses_message


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("12 comida", (12.0, "comida")),
        ("comida 12", (12.0, "comida")),
        ("12.34 en comida", (12.34, "en comida")),
        ("gasto de 12.34", (12.34, "gasto de")),
        ("12,34 en comida", (12.34, "en comida")),
        ("gasto de 12,34", (12.34, "gasto de")),
        ("   12   comida   ", (12.0, "comida")),
        ("comida    12", (12.0, "comida")),
    ],
)
def test_valid_entries(input_str, expected):
    assert parse_expenses_message(input_str) == expected


@pytest.mark.parametrize(
    "input_str",
    [
        "comida 12 34",  # two numbers -> reject
        "12 comida 34",  # two numbers -> reject
        "comida, 12",  # punctuation hugging the space -> reject
        "abc",  # no number
        "12",  # number only (no text)
        "comida12",  # number not separated by space
        "co12 mida",  # number in the middle
        "12comida",  # number stuck to text
        "comida 12.",  # trailing dot isn't a valid decimal
        ".12 comida",  # leading dot not allowed by spec
    ],
)
def test_invalid_entries(input_str):
    assert parse_expenses_message(input_str) is None


def test_types_and_value():
    val, text = parse_expenses_message("45,6 cena")
    assert isinstance(val, float)
    assert isinstance(text, str)
    assert val == pytest.approx(45.6)
    assert text == "cena"
