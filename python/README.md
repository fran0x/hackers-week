# Trading Ladder Web

A minimalist real-time **BTC/USDT** order book built using **Binance market data**, developed in **Python**.  

The application displays market statistics, buy/sell ladders, and recent trades in a **terminal-like web interface**.  

## 🚀 Setup

```bash
# Create and activate a virtual environment with Python 3.11

# Install dependencies
pip install -r requirements.txt
```

## 🎮 Usage

```bash
# Start the application
python app.py

# Access in browser
# Open http://localhost:8050
```

## 📌 Notes  

- The application refreshes market data **every 2 seconds**.  
- The application relies on the **public Binance API** (no API key required).
- It uses the [CCXT library](https://github.com/ccxt/ccxt) to fetch real-time market data from Binance.  
- The web interface is built using [Dash](https://dash.plotly.com/), a Python framework for data visualization applications.  
