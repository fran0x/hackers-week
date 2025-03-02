# Trading Ladders  

Minimalist real-time **BTC/USDT** order books using **Binance** market data.  

## 📋 Prerequisites
- **Python**: 3.11+
- **Rust**: 1.81+

## 📂 Project Structure  

This repository contains two implementations of a real-time order book:

- **[Python](/python)** → Web-based version ([Python README](/python/README.md))  
- **[Rust](/rust)** → Terminal-based version ([Rust README](/rust/README.md))  

## 📌 Features  

Both implementations display:  
✅ OHLC market data & spread  
✅ Order book with **bids (green)** and **asks (red)**  
✅ Recent trades with timestamps  

---

## 🛠️ Getting Started  

To explore the project, follow this sequence:

### 1️⃣ **Try the Command Line API Access**  

Before using the applications, you can fetch Binance data manually:

```bash
# REST API (requires curl and jq)
curl -s "https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=10" | jq

# WebSocket (live data)
cargo install websocat
websocat "wss://stream.binance.com:9443/ws/btcusdt@trade"
```

---

### 2️⃣ **Try the Python Implementation**  

The Python project has multiple branches with increasing functionality:

- **`main` branch** → Displays a **non-interactive order book** with real-time data.
- **`market-order` branch** → Adds support for **placing market orders** with an initial balance.
- **`limit-order` branch** → Further extends `market-order`, allowing **limit orders** as well.

Start by checking out the **main** branch and progress through the others.

---

### 3️⃣ **Try the Rust Implementation**  

For a **terminal-based** experience, explore the Rust project, which provides real-time order book visualization in a CLI environment.
