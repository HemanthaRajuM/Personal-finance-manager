from datetime import date
from decimal import Decimal

import pytest

from utils import parse_amount, parse_date


def test_parse_amount_accepts_positive_value():
    assert parse_amount("1250.5") == Decimal("1250.50")


@pytest.mark.parametrize("value", ["0", "-10", "not-a-number", None])
def test_parse_amount_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        parse_amount(value)


def test_parse_date_accepts_iso_date():
    assert parse_date("2026-08-11") == date(2026, 8, 11)


@pytest.mark.parametrize("value", ["11-08-2026", "2026-13-01", "invalid", None])
def test_parse_date_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        parse_date(value)
