# Trading Ladders  

Minimalist real-time order book interactions with **[Binance](https://www.binance.com) and [Kraken](https://pro.kraken.com/)**.  

## 📋 Prerequisites

- **Platforms**: Linux or MacOS
- **Python**: 3.11+
- **Rust**: 1.81+

```bash
# Rust development
cargo install just
```

## 📂 Project Structure  

This repository contains multiple implementations of a real-time order book interactions:

- **[Binance with Python](/python)** → Web-based version ([Python README](/python/README.md))  
- **[Binance with Rust](/rust)** → Terminal-based version ([Rust README](/rust/README.md))  
- **[Kraken with Python](/kraken)** → Kraken testnet ([Kraken README](/kraken/KRAKEN.md))

The Binance implementations display:  
- OHLC market data, 24h volumes and spread  
- Order book with **bids** (green) and **asks** (red)  
- Recent trades with timestamps  

## 🛠️ Getting Started  

To explore the project, follow this sequence:

### 1️⃣ Try the Command Line API Access

Before using the applications, you can fetch Binance and Kraken data manually:

#### Binance
```bash
# REST API (requires curl and jq)
curl -s "https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=10" | jq

# WebSocket (live data)
cargo install websocat
websocat "wss://stream.binance.com:9443/ws/btcusdt@trade"
```

#### Kraken
```bash
# REST API (requires curl and jq)
curl -X GET "https://demo-futures.kraken.com/derivatives/api/v3/tickers" | jq

# WebSocket (live data)
websocat -E wss://demo-futures.kraken.com/ws/v1

# Send a subscription message:
echo '{ "event":"subscribe", "feed":"ticker", "product_ids":["PI_XRPUSD"] }' | websocat -E wss://demo-futures.kraken.com/ws/v1
```

### 2️⃣ Try the Python Implementation for Binance 

The Python project has multiple branches with increasing functionality:

- **`main` branch** → Displays a **non-interactive order book** with real-time data.
- **`market-order` branch** → Adds support for **placing market orders** with an initial balance.
- **`limit-order` branch** → Further extends `market-order`, allowing **limit orders** as well.

Start by checking out the **main** branch and progress through the others.

### 3️⃣ Try the Rust Implementation for Binance

For a **terminal-based** experience, explore the Rust project, which provides real-time order book visualization in a CLI environment.

### 4️⃣ Explore the Kraken Testnet Integration

Aside from the Binance implementations, this repository also explores the **Kraken testnet integration**, allowing users to:
- Fetch market data and subscribe to live WebSocket updates.
- Place orders programmatically using Kraken's demo environment.
- Experiment with trading strategies using a simulated balance.

Refer to the [Kraken README](/kraken/KRAKEN.md) for more details on interacting with Kraken's testnet.

