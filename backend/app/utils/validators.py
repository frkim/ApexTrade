"""Validation utilities."""

import re
from decimal import Decimal, InvalidOperation
from typing import Any


def validate_symbol(symbol: str) -> bool:
    """Validate trading symbol format.

    Args:
        symbol: Trading pair symbol (e.g., 'BTC/USDT', 'AAPL')

    Returns:
        True if valid, False otherwise
    """
    if not symbol or not isinstance(symbol, str):
        return False

    pattern = r'^[A-Z0-9]+(/[A-Z0-9]+)?$'
    return bool(re.match(pattern, symbol.upper()))


def validate_timeframe(timeframe: str) -> bool:
    """Validate timeframe format.

    Args:
        timeframe: Candlestick timeframe (e.g., '1m', '1h', '1d')

    Returns:
        True if valid, False otherwise
    """
    valid_timeframes = {
        "1m", "3m", "5m", "15m", "30m",
        "1h", "2h", "4h", "6h", "8h", "12h",
        "1d", "3d", "1w", "1M",
    }
    return timeframe in valid_timeframes


def validate_side(side: str) -> bool:
    """Validate order side.

    Args:
        side: Order side ('buy' or 'sell')

    Returns:
        True if valid, False otherwise
    """
    return side.lower() in {"buy", "sell", "long", "short"}


def validate_order_type(order_type: str) -> bool:
    """Validate order type.

    Args:
        order_type: Type of order

    Returns:
        True if valid, False otherwise
    """
    valid_types = {"market", "limit", "stop", "stop_limit", "trailing_stop"}
    return order_type.lower() in valid_types


def validate_quantity(quantity: Any) -> tuple[bool, Decimal | None]:
    """Validate and convert quantity to Decimal.

    Args:
        quantity: Quantity value

    Returns:
        Tuple of (is_valid, decimal_value)
    """
    try:
        if isinstance(quantity, (int, float)):
            value = Decimal(str(quantity))
        elif isinstance(quantity, str):
            value = Decimal(quantity)
        elif isinstance(quantity, Decimal):
            value = quantity
        else:
            return False, None

        if value <= 0:
            return False, None

        return True, value
    except (InvalidOperation, ValueError):
        return False, None


def validate_price(price: Any) -> tuple[bool, Decimal | None]:
    """Validate and convert price to Decimal.

    Args:
        price: Price value

    Returns:
        Tuple of (is_valid, decimal_value)
    """
    try:
        if isinstance(price, (int, float)):
            value = Decimal(str(price))
        elif isinstance(price, str):
            value = Decimal(price)
        elif isinstance(price, Decimal):
            value = price
        else:
            return False, None

        if value < 0:
            return False, None

        return True, value
    except (InvalidOperation, ValueError):
        return False, None


def validate_email(email: str) -> bool:
    """Validate email format.

    Args:
        email: Email address

    Returns:
        True if valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """Validate password strength.

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []

    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")

    if not re.search(r'[A-Z]', password):
        issues.append("Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        issues.append("Password must contain at least one lowercase letter")

    if not re.search(r'\d', password):
        issues.append("Password must contain at least one digit")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append("Password must contain at least one special character")

    return len(issues) == 0, issues


def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize a string value.

    Args:
        value: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not value:
        return ""

    sanitized = value.strip()
    sanitized = re.sub(r'<[^>]+>', '', sanitized)
    sanitized = sanitized[:max_length]

    return sanitized


def validate_uuid(uuid_string: str) -> bool:
    """Validate UUID format.

    Args:
        uuid_string: UUID string to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    return bool(re.match(pattern, uuid_string.lower()))
