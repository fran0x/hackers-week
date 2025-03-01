# Binance BTC/USDT Simple Ladder

A minimalist real-time BTC/USDT order book from Binance data.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
python app.py

# Access in browser
# Open http://localhost:8050
```

## Notes

The application refreshes data every 2 seconds and uses the public Binance API (no API key required). For production use, consider implementing rate limiting and error handling for API requests.