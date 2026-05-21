#!/usr/bin/env python3
"""
cli.py — Binance Futures Testnet Trading Bot
============================================

Entry point for placing futures orders via the command line.

Usage examples
--------------
# MARKET BUY
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# LIMIT SELL
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3500

# STOP_LIMIT BUY (bonus)
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT \\
              --quantity 0.001 --price 62000 --stop_price 61500
"""

import argparse
import sys

from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.client import create_client
from bot.logging_config import get_logger
from bot.orders import dispatch_order
from bot.validators import validate_all

logger = get_logger("cli")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet Trading Bot — place MARKET, LIMIT, or STOP_LIMIT orders.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cli.py --symbol BTCUSDT --side BUY  --type MARKET     --quantity 0.001\n"
            "  python cli.py --symbol ETHUSDT --side SELL --type LIMIT       --quantity 0.01  --price 3500\n"
            "  python cli.py --symbol BTCUSDT --side BUY  --type STOP_LIMIT  --quantity 0.001 --price 62000 --stop_price 61500\n"
        ),
    )

    parser.add_argument(
        "--symbol",
        required=True,
        metavar="SYMBOL",
        help="Trading pair symbol, e.g. BTCUSDT",
    )
    parser.add_argument(
        "--side",
        required=True,
        metavar="SIDE",
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        metavar="TYPE",
        help="Order type: MARKET | LIMIT | STOP_LIMIT",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        type=float,
        metavar="QTY",
        help="Order quantity (must be > 0)",
    )
    parser.add_argument(
        "--price",
        type=float,
        default=None,
        metavar="PRICE",
        help="Limit price — required for LIMIT and STOP_LIMIT orders",
    )
    parser.add_argument(
        "--stop_price",
        type=float,
        default=None,
        metavar="STOP_PRICE",
        help="Stop trigger price — required for STOP_LIMIT orders",
    )

    return parser


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logger.debug("Raw CLI args: %s", vars(args))

    # ── 1. Validate inputs ──────────────────────────────────────────────────
    try:
        validated = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        print(f"\n❌  Validation Error: {exc}\n")
        sys.exit(1)

    logger.debug("Validated params: %s", validated)

    # ── 2. Initialise Binance client ────────────────────────────────────────
    try:
        client = create_client()
    except EnvironmentError as exc:
        logger.error("Environment error: %s", exc)
        print(f"\n❌  Environment Error: {exc}\n")
        sys.exit(1)

    # ── 3. Dispatch order ───────────────────────────────────────────────────
    try:
        response = dispatch_order(
            client=client,
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["order_type"],
            quantity=validated["quantity"],
            price=validated["price"],
            stop_price=validated["stop_price"],
        )
        print("✅  Order placed successfully!\n")
        logger.info(
            "Order placed successfully | orderId=%s | status=%s",
            response.get("orderId"),
            response.get("status"),
        )

    except BinanceAPIException as exc:
        logger.error(
            "Binance API error | code=%s | message=%s", exc.code, exc.message
        )
        print(f"\n❌  Binance API Error [{exc.code}]: {exc.message}\n")
        sys.exit(1)

    except BinanceRequestException as exc:
        logger.error("Network/request error: %s", exc)
        print(f"\n❌  Network Error: {exc}\n")
        sys.exit(1)

    except ValueError as exc:
        logger.error("Order dispatch error: %s", exc)
        print(f"\n❌  Order Error: {exc}\n")
        sys.exit(1)

    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error: %s", exc)
        print(f"\n❌  Unexpected Error: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
