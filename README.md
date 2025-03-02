# Trading Ladders  

Minimalist real-time **BTC/USDT** order books using **Binance** data.  

## 📋 Prerequisites
- **Python version**: 3.11+
- **Rust version**: 1.81+

## 📂 Structure  

- [python](/python) → Web-based, see [Python README](/python/README.md)
- [rust](/rust) → Terminal-based, see [Rust README](/rust/README.md)

## 📌 Notes  

Both versions display:  
- OHLC market data & spread  
- Order book with bids (green) & asks (red)  
- Recent trades with timestamps  

## 🖥️ Command Line Access

Direct API access using just command line tools:

```bash
# REST API (requires curl and jq)
curl -s "https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=10" | jq

# WebSocket (live data)
cargo install websocat
websocat "wss://stream.binance.com:9443/ws/btcusdt@trade"
```

## 🎯 Limit Order Execution

The trading ladder supports **placing limit orders**.

The execution follows these special rules:

- If a **buy order** is placed above the **worst sell price**, the **worst sell price** will be taken.
- If a **sell order** is placed below the **worst buy price**, the **worst buy price** will be taken.

This ensures that limit orders interact with the order book efficiently, preventing orders from being placed in unrealistic price levels.

