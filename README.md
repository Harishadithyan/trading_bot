# Binance Futures Testnet Trading Bot

A lightweight Python CLI application for placing orders on the **Binance Futures Testnet (USDT-M)**.
This project supports multiple order types including **Market**, **Limit**, and **Stop-Limit** orders with proper validation and logging.

---

## Features

* Place Binance Futures Testnet orders
* Supports:

  * Market Orders
  * Limit Orders
  * Stop-Limit Orders
* Command-line interface (CLI)
* Input validation
* Logging support
* Modular project structure

---

## Project Structure

```bash
.
├── .env                  # API credentials
├── cli.py                # CLI entry point
├── client.py             # Binance API client setup
├── logging_config.py     # Logging configuration
├── orders.py             # Order execution logic
├── validators.py         # Input validation helpers
├── requirements.txt      # Dependencies
└── README.md             # Documentation
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <project-folder>
```

---

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / Mac

```bash
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_secret_key
```

Get your testnet API keys from:

* Binance Futures Testnet

---

## Running the Application

The application is executed using:

```bash
python cli.py [OPTIONS]
```

---

# Supported Order Types

---

## 1. Market Order

Executes immediately at the current market price.

### Example

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

---

## 2. Limit Order

Executes only at the specified price or better.

### Example

```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3500
```

---

## 3. Stop-Limit Order

Triggers a limit order when the stop price is reached.

### Example

```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.001 --price 62000 --stop_price 61500
```

---

# CLI Arguments

| Argument       | Description                         | Required    |
| -------------- | ----------------------------------- | ----------- |
| `--symbol`     | Trading pair (e.g., BTCUSDT)        | Yes         |
| `--side`       | BUY or SELL                         | Yes         |
| `--type`       | MARKET, LIMIT, STOP_LIMIT           | Yes         |
| `--quantity`   | Order quantity                      | Yes         |
| `--price`      | Price for LIMIT / STOP_LIMIT orders | Conditional |
| `--stop_price` | Trigger price for STOP_LIMIT orders | Conditional |

---

# Example Commands

### Market Buy

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Limit Sell

```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3500
```

### Stop-Limit Buy

```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.001 --price 62000 --stop_price 61500
```

---

# Validation Rules

* `LIMIT` orders require `--price`
* `STOP_LIMIT` orders require:

  * `--price`
  * `--stop_price`
* Quantity must be greater than zero
* Side must be:

  * `BUY`
  * `SELL`

---

# Logging

The application uses centralized logging via:

```bash
logging_config.py
```

Logs help track:

* Order requests
* Validation errors
* API responses
* Exceptions

---

# Requirements

Example dependencies:

```txt
python-binance
python-dotenv
```

Install all dependencies using:

```bash
pip install -r requirements.txt
```

---

# Notes

* This project is intended for **Binance Futures Testnet only**
* Do NOT use real exchange keys
* Ensure your testnet account has sufficient balance

---

# Future Improvements

* Add Take Profit / Stop Loss support
* WebSocket price monitoring
* Strategy automation
* Docker support
* Unit testing
* Order history tracking

---

# Author

Harish Adithyan
