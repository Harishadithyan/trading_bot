"""
Binance Futures Testnet client wrapper.

Loads credentials from the environment (via .env) and returns a configured
python-binance Client pointed at the Futures Testnet base URL.
"""

import os
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from dotenv import load_dotenv

from bot.logging_config import get_logger

logger = get_logger(__name__)

# Binance Futures Testnet REST base URL
FUTURES_TESTNET_URL = "https://testnet.binancefuture.com"


def create_client() -> Client:
    """
    Build and return an authenticated Binance Client configured for the
    Futures Testnet.

    Reads API_KEY and API_SECRET from the environment (or from a .env file
    located in the project root).

    Raises:
        EnvironmentError: If either credential is missing.
        BinanceAPIException / BinanceRequestException: On connectivity issues.
    """
    # Load .env from the project root (two levels up from this file)
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    load_dotenv(dotenv_path=env_path)

    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    if not api_key or not api_secret:
        raise EnvironmentError(
            "API_KEY and API_SECRET must be set in your .env file or environment."
        )

    logger.debug("Creating Binance Futures Testnet client …")

    # Override the default REST endpoint to hit the testnet
    client = Client(
        api_key=api_key,
        api_secret=api_secret,
        testnet=False,  # We manually set the URL below
    )

    # Point all futures REST calls at the testnet
    client.FUTURES_URL = FUTURES_TESTNET_URL + "/fapi"
    client.API_URL = FUTURES_TESTNET_URL + "/fapi"

    logger.info("Binance Futures Testnet client initialised successfully.")
    return client
