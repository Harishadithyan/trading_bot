"""
Order placement logic for Binance Futures Testnet.

Supports:
  - MARKET orders
  - LIMIT orders
  - STOP_LIMIT orders  (bonus)

Each public function accepts a python-binance Client and the validated
order parameters, logs the full request/response, and returns the raw
response dict from the Binance API.
"""

import time
from typing import Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.logging_config import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Retry configuration
# ---------------------------------------------------------------------------
_MAX_RETRIES = 3
_RETRY_DELAY_SECS = 2  # seconds between retries


def _retry(fn, *args, **kwargs):
    """
    Call *fn* with the given arguments, retrying up to _MAX_RETRIES times on
    transient network errors (BinanceRequestException / generic exceptions).
    BinanceAPIException (exchange-level errors) are NOT retried — they indicate
    a problem with the order parameters.
    """
    last_exc: Optional[Exception] = None

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            return fn(*args, **kwargs)
        except BinanceAPIException:
            # Exchange rejected the request — no point retrying
            raise
        except (BinanceRequestException, Exception) as exc:
            last_exc = exc
            logger.warning(
                "Attempt %d/%d failed: %s — retrying in %ss …",
                attempt,
                _MAX_RETRIES,
                exc,
                _RETRY_DELAY_SECS,
            )
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_DELAY_SECS)

    raise last_exc  # re-raise the last exception after exhausting retries


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _log_request(order_type: str, params: dict) -> None:
    logger.info("ORDER REQUEST  | type=%-12s | params=%s", order_type, params)


def _log_response(response: dict) -> None:
    logger.info("ORDER RESPONSE | %s", response)


def _print_summary(params: dict) -> None:
    """Pretty-print the order parameters before submitting."""
    print("\n" + "=" * 60)
    print("  ORDER SUMMARY")
    print("=" * 60)
    for key, value in params.items():
        if value is not None:
            print(f"  {key:<15}: {value}")
    print("=" * 60)


def _print_result(response: dict) -> None:
    """Pretty-print the relevant fields from the Binance response."""
    print("\n" + "=" * 60)
    print("  ORDER RESULT")
    print("=" * 60)
    print(f"  orderId      : {response.get('orderId', 'N/A')}")
    print(f"  status       : {response.get('status', 'N/A')}")
    print(f"  executedQty  : {response.get('executedQty', 'N/A')}")

    avg_price = response.get("avgPrice") or response.get("price")
    if avg_price and float(avg_price) > 0:
        print(f"  avgPrice     : {avg_price}")

    print(f"  symbol       : {response.get('symbol', 'N/A')}")
    print(f"  side         : {response.get('side', 'N/A')}")
    print(f"  type         : {response.get('type', 'N/A')}")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def place_market_order(
    client: Client,
    symbol: str,
    side: str,
    quantity: float,
) -> dict:
    """
    Place a Futures MARKET order.

    Args:
        client:   Authenticated Binance client.
        symbol:   Trading pair (e.g. "BTCUSDT").
        side:     "BUY" or "SELL".
        quantity: Contract quantity.

    Returns:
        Raw Binance API response dict.
    """
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
    }

    _print_summary(params)
    _log_request("MARKET", params)

    response = _retry(
        client.futures_create_order,
        symbol=symbol,
        side=side,
        type="MARKET",
        quantity=quantity,
    )

    _log_response(response)
    _print_result(response)
    return response


def place_limit_order(
    client: Client,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC",
) -> dict:
    """
    Place a Futures LIMIT order.

    Args:
        client:         Authenticated Binance client.
        symbol:         Trading pair.
        side:           "BUY" or "SELL".
        quantity:       Contract quantity.
        price:          Limit price.
        time_in_force:  "GTC" (Good Till Cancel) by default.

    Returns:
        Raw Binance API response dict.
    """
    params = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "quantity": quantity,
        "price": price,
        "timeInForce": time_in_force,
    }

    _print_summary(params)
    _log_request("LIMIT", params)

    response = _retry(
        client.futures_create_order,
        symbol=symbol,
        side=side,
        type="LIMIT",
        quantity=quantity,
        price=price,
        timeInForce=time_in_force,
    )

    _log_response(response)
    _print_result(response)
    return response


def place_stop_limit_order(
    client: Client,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    stop_price: float,
    time_in_force: str = "GTC",
) -> dict:
    """
    Place a Futures STOP_LIMIT order (bonus feature).

    A STOP_LIMIT order triggers a LIMIT order once *stop_price* is reached.

    Args:
        client:      Authenticated Binance client.
        symbol:      Trading pair.
        side:        "BUY" or "SELL".
        quantity:    Contract quantity.
        price:       Limit price executed after stop is triggered.
        stop_price:  Price that triggers the order.

    Returns:
        Raw Binance API response dict.
    """
    params = {
        "symbol": symbol,
        "side": side,
        "type": "STOP",
        "quantity": quantity,
        "price": price,
        "stopPrice": stop_price,
        "timeInForce": time_in_force,
    }

    _print_summary(params)
    _log_request("STOP_LIMIT", params)

    response = _retry(
        client.futures_create_order,
        symbol=symbol,
        side=side,
        type="STOP",
        quantity=quantity,
        price=price,
        stopPrice=stop_price,
        timeInForce=time_in_force,
    )

    _log_response(response)
    _print_result(response)
    return response


def dispatch_order(
    client: Client,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> dict:
    """
    Route the validated parameters to the appropriate order function.

    Args:
        client:      Authenticated Binance client.
        symbol:      Trading pair.
        side:        "BUY" or "SELL".
        order_type:  "MARKET", "LIMIT", or "STOP_LIMIT".
        quantity:    Contract quantity.
        price:       Required for LIMIT / STOP_LIMIT.
        stop_price:  Required for STOP_LIMIT.

    Returns:
        Raw Binance API response dict.

    Raises:
        ValueError: For unsupported order types (should be caught by validators).
    """
    order_type = order_type.upper()

    if order_type == "MARKET":
        return place_market_order(client, symbol, side, quantity)

    elif order_type == "LIMIT":
        return place_limit_order(client, symbol, side, quantity, price)

    elif order_type == "STOP_LIMIT":
        return place_stop_limit_order(
            client, symbol, side, quantity, price, stop_price
        )

    else:
        raise ValueError(f"Unsupported order type: {order_type}")
