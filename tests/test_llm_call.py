import pytest
from unittest.mock import MagicMock, patch

from src.llm_call import ExpenseExtraction, create_context, llm_call, make_expense_model

CATS = ["COMIDA", "TRANSPORTE", "OTROS"]


# ── make_expense_model ─────────────────────────────────────────────────────────

def test_make_expense_model_is_basemodel_subclass():
    from pydantic import BaseModel
    assert issubclass(make_expense_model(CATS), BaseModel)


def test_make_expense_model_has_required_fields():
    Model = make_expense_model(CATS)
    assert set(Model.model_fields) == {"value", "category", "currency"}


def test_make_expense_model_accepts_valid_category():
    Model = make_expense_model(CATS)
    instance = Model(value=100.0, category="COMIDA", currency="ARS")
    assert instance.category == "COMIDA"


def test_make_expense_model_rejects_invalid_category():
    Model = make_expense_model(CATS)
    with pytest.raises(Exception):
        Model(value=100.0, category="INVALID_CAT", currency="ARS")


# ── create_context ─────────────────────────────────────────────────────────────

def test_create_context_returns_string():
    assert isinstance(create_context(CATS), str)


def test_create_context_includes_all_categories():
    ctx = create_context(CATS)
    for cat in CATS:
        assert cat in ctx


# ── llm_call ───────────────────────────────────────────────────────────────────

def test_llm_call_returns_expense_extraction():
    FixedModel = make_expense_model(CATS)
    mock_parsed = FixedModel(value=50.0, category="COMIDA", currency="ARS")
    mock_response = MagicMock()
    mock_response.output_parsed = mock_parsed

    with patch("src.llm_call.client") as mock_client, \
         patch("src.llm_call.make_expense_model", return_value=FixedModel):
        mock_client.responses.parse.return_value = mock_response
        result = llm_call("almuerzo 50", CATS)

    assert isinstance(result, ExpenseExtraction)
    assert result.value == 50.0
    assert result.category == "COMIDA"
    assert result.currency == "ARS"


def test_llm_call_passes_message_to_api():
    FixedModel = make_expense_model(CATS)
    mock_parsed = FixedModel(value=10.0, category="TRANSPORTE", currency="ARS")
    mock_response = MagicMock()
    mock_response.output_parsed = mock_parsed

    with patch("src.llm_call.client") as mock_client, \
         patch("src.llm_call.make_expense_model", return_value=FixedModel):
        mock_client.responses.parse.return_value = mock_response
        llm_call("taxi al trabajo", CATS)

    call_kwargs = mock_client.responses.parse.call_args.kwargs
    user_contents = [m["content"] for m in call_kwargs["input"] if m["role"] == "user"]
    assert "taxi al trabajo" in user_contents[0]


def test_llm_call_maps_currency():
    FixedModel = make_expense_model(CATS)
    mock_parsed = FixedModel(value=20.0, category="OTROS", currency="USD")
    mock_response = MagicMock()
    mock_response.output_parsed = mock_parsed

    with patch("src.llm_call.client") as mock_client, \
         patch("src.llm_call.make_expense_model", return_value=FixedModel):
        mock_client.responses.parse.return_value = mock_response
        result = llm_call("something in USD", CATS)

    assert result.currency == "USD"
