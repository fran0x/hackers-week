# Kraken Perpetuals Testnet Demo

This document explains how to interact with Kraken's perpetual futures testnet. It includes manual operations, API interactions, and basic Python scripts for fetching market data and placing orders programmatically.

## Environment Setup

All required tools can be installed in a MacOS using [Homebrew](https://brew.sh/), including:
- [Google Chrome](https://www.google.com/chrome/)
- [curl](https://curl.se/)
- [websocat](https://github.com/vi/websocat)
- [jq](https://stedolan.github.io/jq/)
- [Python](https://www.python.org/)

The built-in Vim editor can be used for writing scripts.

## Kraken Websites

The following websites are relevant to learn more about Kraken and about its API and testnet:
1. [Kraken Pro](https://pro.kraken.com/)
2. [Kraken BTC/USD Trading](https://pro.kraken.com/app/trade/btc-usd)
3. [Kraken API Documentation](https://docs.kraken.com/api/)
4. [Kraken Futures Testnet](https://demo-futures.kraken.com/)

## Kraken Futures Testnet Overview

Kraken's demo futures platform allows users to:
- Create a test account with an initial balance.
- Place orders manually.
- Generate API keys for programmatic trading.

## Command-Line Scripts

The following scripts can be executed via command line:

### Fetching Market Data via REST API
```sh
curl -X GET "https://demo-futures.kraken.com/derivatives/api/v3/tickers" | jq
```

### WebSocket Market Data Streaming
```sh
websocat -E wss://demo-futures.kraken.com/ws/v1
```

Then, send the following JSON message:
```json
{ "event":"subscribe", "feed":"ticker", "product_ids":["PI_XRPUSD"] }
```

## Python Scripts

### Fetching Market Data

This script retrieves Kraken Futures market data using `ccxt`:
```python
from pprint import pprint
import ccxt

exchange = ccxt.krakenfutures()
markets = exchange.load_markets()

print(exchange.name, "supports the following methods:")
pprint(exchange.has)

print(exchange.name, "supports the following trading symbols:")
for symbol in exchange.symbols:
    print(symbol)

print("Fetching order book for selected symbol:")
symbol = 'BTC/USD:USD'
orderbook = exchange.fetch_order_book(symbol)
pprint(orderbook)
```

### Placing Orders

This script interacts with Kraken Futures to place orders programmatically:
```python
import ccxt
import time

exchange_params = {
    "API_KEY": "PASTE_PUBLIC_KEY_HERE",
    "API_KEY_SECRET": "PASTE_PRIVATE_KEY_HERE",
    "TESTNET": True,
}

exchange = ccxt.krakenfutures(
    {
        "apiKey": exchange_params["API_KEY"],
        "secret": exchange_params["API_KEY_SECRET"],
        "enableRateLimit": True,
        'options': {
            'defaultType': 'future',
        },
    }
)

exchange.set_sandbox_mode(True)
balance = exchange.fetch_balance({"type": "future","marginType": "isolated"})

market = exchange.load_markets()
print(market)

symbol = "BTC/USD:BTC"

current_price = exchange.fetch_ticker(symbol)

market_order = exchange.create_order(symbol, 'market', 'buy', 1)
limit_order = exchange.create_order(symbol, 'limit', 'buy', 1, 60000)
sl_order = exchange.create_order(symbol, 'limit', 'sell', 1, None, {"stopLossPrice": "58000", "reduceOnly": True})
tp_order = exchange.create_order(symbol, 'limit', 'sell', 1, None, {"takeProfitPrice": "70000", "reduceOnly": True})
```

It is recommended to have the [Kraken Futures Testnet Web Interface](https://demo-futures.kraken.com/) open while running these scripts to see the outcome live.

## Next Steps

- Implement a trading strategy that decides when to buy, sell, or cancel orders based on market data.
- Enhance risk management by integrating stop-loss and take-profit mechanisms.
- Experiment with different order types and leverage settings.

