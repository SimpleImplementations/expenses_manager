import io

from src.db import ExpenseRow
from src.rows_to_csv_bytes import rows_to_csv_bytes


def test_returns_bytesio():
    assert isinstance(rows_to_csv_bytes([]), io.BytesIO)


def test_filename_attribute():
    bio = rows_to_csv_bytes([])
    assert bio.name.startswith("expenses_")
    assert bio.name.endswith(".csv")


def test_empty_has_header():
    content = rows_to_csv_bytes([]).read().decode("utf-8")
    assert "Fecha" in content
    assert "Monto" in content
    assert "Moneda" in content


def test_row_content():
    rows = [ExpenseRow(date="2024-01-15", value=100.0, category="SUPERMERCADO", currency="ARS", message="compras")]
    content = rows_to_csv_bytes(rows).read().decode("utf-8")
    assert "2024-01-15" in content
    assert "100.0" in content
    assert "SUPERMERCADO" in content
    assert "ARS" in content
    assert "compras" in content


def test_multiple_rows():
    rows = [
        ExpenseRow(date="2024-01-01", value=50.0, category="TAXI", currency="ARS", message="taxi"),
        ExpenseRow(date="2024-01-02", value=200.0, category="SUPERMERCADO", currency="USD", message="super"),
    ]
    content = rows_to_csv_bytes(rows).read().decode("utf-8")
    assert "TAXI" in content
    assert "SUPERMERCADO" in content
    assert "USD" in content


def test_fractional_value():
    rows = [ExpenseRow(date="2024-01-01", value=99.99, category="OTROS", currency="ARS", message="x")]
    content = rows_to_csv_bytes(rows).read().decode("utf-8")
    assert "99.99" in content
