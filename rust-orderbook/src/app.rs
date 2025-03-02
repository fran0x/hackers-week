use crate::binance::{BinanceClient, OrderBook, Side, Ticker, Trade};
use anyhow::Result;
use chrono::{DateTime, Local, Utc};
use rust_decimal::Decimal;
use std::cmp::{max, min};

pub struct App {
    client: BinanceClient,
    pub order_book: Option<OrderBook>,
    pub ticker: Option<Ticker>,
    pub trades: Vec<Trade>,
    pub last_update: DateTime<Local>,
    pub status_message: String,
    pub error: Option<String>,
}

impl App {
    pub fn new() -> Self {
        Self {
            client: BinanceClient::new(),
            order_book: None,
            ticker: None,
            trades: Vec::new(),
            last_update: Local::now(),
            status_message: "Loading data...".to_string(),
            error: None,
        }
    }

    pub async fn update(&mut self) -> Result<()> {
        match self.fetch_data().await {
            Ok(_) => {
                self.last_update = Local::now();
                self.status_message = format!("Last updated: {}", self.last_update.format("%H:%M:%S"));
                self.error = None;
            }
            Err(e) => {
                self.error = Some(format!("Error: {}", e));
            }
        }
        Ok(())
    }

    pub async fn refresh_now(&mut self) -> Result<()> {
        self.status_message = "Refreshing...".to_string();
        self.update().await
    }

    async fn fetch_data(&mut self) -> Result<()> {
        // Parallel fetching would be better but for simplicity we'll do it sequentially
        let order_book = self.client.get_order_book(15).await?;
        let ticker = self.client.get_ticker().await?;
        let trades = self.client.get_recent_trades(15).await?;

        self.order_book = Some(order_book);
        self.ticker = Some(ticker);
        self.trades = trades;

        Ok(())
    }

    pub fn calculate_spread(&self) -> Option<Decimal> {
        if let Some(order_book) = &self.order_book {
            if !order_book.asks.is_empty() && !order_book.bids.is_empty() {
                let lowest_ask = order_book.asks.iter().map(|a| a.price).min()?;
                let highest_bid = order_book.bids.iter().map(|b| b.price).max()?;
                return Some(lowest_ask - highest_bid);
            }
        }
        None
    }
}