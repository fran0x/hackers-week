# BTC/USDT Order Book Visualizer

A minimalist real-time BTC/USDT order book from Binance data.

## Implementations

This project provides two implementations:
- **Python (Web)**: Main implementation using Dash and Plotly (this directory)
- **Rust (Terminal)**: Alternative TUI version in the `rust-orderbook/` directory

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