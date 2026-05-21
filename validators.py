"""
Input validators for CLI arguments before they reach the Binance API.
All validators raise ValueError with a human-readable message on failure.
"""

from typing import Optional

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}


def validate_side(side: str) -> str:
    """Ensure order side is BUY or SELL."""
    side = side.upper()
    if side not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}"
        )
    return side


def validate_order_type(order_type: str) -> str:
    """Ensure order type is MARKET, LIMIT, or STOP_LIMIT."""
    order_type = order_type.upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}"
        )
    return order_type


def validate_quantity(quantity: float) -> float:
    """Ensure quantity is a positive number."""
    if quantity <= 0:
        raise ValueError(f"Quantity must be greater than zero. Got: {quantity}")
    return quantity


def validate_price(price: Optional[float], order_type: str) -> Optional[float]:
    """
    For LIMIT and STOP_LIMIT orders, price must be supplied and positive.
    For MARKET orders, price should be None (ignored by the exchange).
    """
    if order_type in {"LIMIT", "STOP_LIMIT"}:
        if price is None:
            raise ValueError(
                f"--price is required for {order_type} orders."
            )
        if price <= 0:
            raise ValueError(
                f"Price must be greater than zero for {order_type} orders. Got: {price}"
            )
    return price


def validate_stop_price(
    stop_price: Optional[float], order_type: str
) -> Optional[float]:
    """For STOP_LIMIT orders, stop_price must be supplied and positive."""
    if order_type == "STOP_LIMIT":
        if stop_price is None:
            raise ValueError("--stop_price is required for STOP_LIMIT orders.")
        if stop_price <= 0:
            raise ValueError(
                f"Stop price must be greater than zero. Got: {stop_price}"
            )
    return stop_price


def validate_symbol(symbol: str) -> str:
    """Basic sanity check — symbols must be non-empty strings."""
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("--symbol cannot be empty.")
    return symbol


def validate_all(
    *,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> dict:
    """
    Run all validators and return a dict of sanitized values.
    Raises ValueError on the first validation failure.
    """
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)
    price = validate_price(price, order_type)
    stop_price = validate_stop_price(stop_price, order_type)

    return {
        "symbol": symbol,
        "side": side,
        "order_type": order_type,
        "quantity": quantity,
        "price": price,
        "stop_price": stop_price,
    }
