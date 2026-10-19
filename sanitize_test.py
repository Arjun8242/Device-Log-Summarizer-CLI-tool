
from sanitize import sanitize_readings


def test_mixed_input():
    result = sanitize_readings(["12.5", None, -3, "abc", 600, "499"])
    assert result == [12.5, 500.0, 499.0]
    assert all(isinstance(x, float) for x in result)  # fails until you fix min(..., 500.0)


def test_empty_and_none_input():
    assert sanitize_readings([]) == []
    assert sanitize_readings(None) == []  # fails until you add the guard


def test_all_invalid():
    assert sanitize_readings([None, "x", -1]) == []


def test_edge_values():
    # 0 and exactly 500.0 are valid; nan/inf are dropped
    assert sanitize_readings([0, 500.0, float("nan"), float("inf")]) == [0.0, 500.0]