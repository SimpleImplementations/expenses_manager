from src.utils import to_int_if_whole


def test_whole_float_returns_int():
    result = to_int_if_whole(5.0)
    assert result == 5
    assert isinstance(result, int)


def test_fractional_returns_float():
    result = to_int_if_whole(5.5)
    assert result == 5.5
    assert isinstance(result, float)


def test_zero():
    result = to_int_if_whole(0.0)
    assert result == 0
    assert isinstance(result, int)


def test_negative_whole():
    result = to_int_if_whole(-3.0)
    assert result == -3
    assert isinstance(result, int)


def test_large_whole():
    assert to_int_if_whole(100000.0) == 100000


def test_small_fraction_stays_float():
    result = to_int_if_whole(1.01)
    assert isinstance(result, float)
