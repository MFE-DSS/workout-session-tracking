"""Unit tests for app.services.form_parsing."""
from __future__ import annotations

from app.services.form_parsing import (
    checkbox,
    clean_str,
    enum_int,
    enum_str,
    to_float,
    to_int,
)

# ---------------------------------------------------------------------------
# to_float — B01 decimal separator support (point AND comma)
# ---------------------------------------------------------------------------


def test_to_float_accepts_dot():
    assert to_float("12.5") == 12.5


def test_to_float_accepts_comma():
    assert to_float("12,5") == 12.5


def test_to_float_accepts_integer_string():
    assert to_float("60") == 60.0


def test_to_float_accepts_negative():
    assert to_float("-2.5") == -2.5


def test_to_float_rejects_letters():
    assert to_float("abc") is None


def test_to_float_rejects_empty():
    assert to_float("") is None


def test_to_float_rejects_none():
    assert to_float(None) is None


def test_to_float_strips_whitespace():
    assert to_float(" 12.5 ") == 12.5


def test_to_float_handles_comma_with_whitespace():
    assert to_float(" 12,5 ") == 12.5


def test_to_float_rejects_double_separator():
    # "12.5.6" → float raises ValueError → None
    assert to_float("12.5.6") is None


# ---------------------------------------------------------------------------
# to_int
# ---------------------------------------------------------------------------


def test_to_int_accepts_integer_string():
    assert to_int("10") == 10


def test_to_int_accepts_float_string():
    # "10.5" → int(float("10.5")) = 10
    assert to_int("10.5") == 10


def test_to_int_rejects_empty():
    assert to_int("") is None


def test_to_int_rejects_letters():
    assert to_int("abc") is None


# ---------------------------------------------------------------------------
# clean_str
# ---------------------------------------------------------------------------


def test_clean_str_trims():
    assert clean_str("  hello  ") == "hello"


def test_clean_str_empty_returns_none():
    assert clean_str("   ") is None


def test_clean_str_truncates():
    assert clean_str("abcdef", max_length=3) == "abc"


# ---------------------------------------------------------------------------
# enum_str / enum_int
# ---------------------------------------------------------------------------


def test_enum_str_allowed():
    assert enum_str("high", {"high", "medium", "low"}) == "high"


def test_enum_str_disallowed():
    assert enum_str("xxx", {"high", "low"}) is None


def test_enum_int_allowed():
    assert enum_int("80", {100, 80, 50}) == 80


def test_enum_int_disallowed():
    assert enum_int("75", {100, 80, 50}) is None


# ---------------------------------------------------------------------------
# checkbox
# ---------------------------------------------------------------------------


def test_checkbox_on():
    assert checkbox("1") is True
    assert checkbox("true") is True
    assert checkbox("on") is True


def test_checkbox_off():
    assert checkbox(None) is False
    assert checkbox("") is False
    assert checkbox("0") is False
    assert checkbox("false") is False
