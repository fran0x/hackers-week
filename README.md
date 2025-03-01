# UMA Trading Order Book

A minimalist real-time BTC/USDT order book visualization using Python, Dash, and Binance data.

## Features

- Real-time order book data from Binance
- Terminal-style interface with black background and monospace fonts
- Order book display:
  - Asks (sell orders) in red at the top
  - Current price highlighted in yellow in the middle
  - Bids (buy orders) in green at the bottom
- Recent trades display showing real-time market activity
- Market information with OHLC, volume, spread, and change

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Start the application:
   ```
   python app.py
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:8050
   ```

## Notes

- The application refreshes data every 2 seconds
- The application uses the public Binance API (no API key required for this functionality)
- For production use, consider implementing rate limiting and error handling for API requests