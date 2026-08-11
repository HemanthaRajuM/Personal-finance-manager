from datetime import date
from decimal import Decimal, InvalidOperation


def parse_amount(value):
    try:
        parsed = Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Amount must be a valid number")
    if not parsed.is_finite() or parsed <= 0:
        raise ValueError("Amount must be greater than zero")
    return parsed


def parse_date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError("Date must use YYYY-MM-DD format")
