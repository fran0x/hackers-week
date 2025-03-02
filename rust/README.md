# Trading Ladder TUI

A minimalist real-time **BTC/USDT** order book built using **Binance market data**, developed in **Rust**.  

The application displays **market statistics, buy/sell ladders, and recent trades** in a **terminal-based interface**.  

## 🚀 Setup  

Explore the available commands using [`just`](https://github.com/casey/just) for building and running the project.  

```bash
# Build the application
just build

# Start the application
./target/release/btc-orderbook
```

## 🎮 Usage  

```bash
# Start the application
just run
```

- **`q`** → Quit  
- **`r`** → Refresh data  

## 📌 Notes  

- The application **refreshes market data every second**.  
- It uses the **public Binance API** (no API key required).  
- It is built using **[Tokio](https://tokio.rs/)**, an asynchronous runtime for Rust.  
- The **terminal UI** is powered by **[Ratatui](https://github.com/ratatui-org/ratatui)** and **[Crossterm](https://github.com/crossterm-rs/crossterm)** for handling rendering and user input.  
- REST requests to Binance’s public API are made using **[Reqwest](https://github.com/seanmonstar/reqwest)**. 