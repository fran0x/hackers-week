use anyhow::Result;
use chrono::{DateTime, Utc};
use rust_decimal::Decimal;
use serde::{Deserialize, Serialize};
use std::cmp::Ordering;

pub const SYMBOL: &str = "BTCUSDT";
const BASE_URL: &str = "https://api.binance.com/api/v3";

pub struct BinanceClient {
    client: reqwest::Client,
}

impl BinanceClient {
    pub fn new() -> Self {
        Self {
            client: reqwest::Client::new(),
        }
    }

    pub async fn get_order_book(&self, limit: usize) -> Result<OrderBook> {
        let url = format!("{}/depth?symbol={}&limit={}", BASE_URL, SYMBOL, limit);
        let response = self.client.get(&url).send().await?;
        let order_book = response.json::<OrderBookResponse>().await?;
        
        Ok(OrderBook {
            bids: order_book.bids.into_iter().map(|b| Order::new(b[0], b[1], Side::Buy)).collect(),
            asks: order_book.asks.into_iter().map(|a| Order::new(a[0], a[1], Side::Sell)).collect(),
        })
    }

    pub async fn get_ticker(&self) -> Result<Ticker> {
        let url = format!("{}/ticker/24hr?symbol={}", BASE_URL, SYMBOL);
        let response = self.client.get(&url).send().await?;
        let ticker = response.json::<TickerResponse>().await?;
        
        Ok(Ticker {
            last_price: ticker.last_price,
            open_price: ticker.open_price,
            high_price: ticker.high_price,
            low_price: ticker.low_price,
            volume: ticker.volume,
            price_change_percent: ticker.price_change_percent,
        })
    }

    pub async fn get_recent_trades(&self, limit: usize) -> Result<Vec<Trade>> {
        let url = format!("{}/trades?symbol={}&limit={}", BASE_URL, SYMBOL, limit);
        let response = self.client.get(&url).send().await?;
        let trades = response.json::<Vec<TradeResponse>>().await?;
        
        Ok(trades
            .into_iter()
            .map(|t| Trade {
                id: t.id,
                price: t.price,
                qty: t.qty,
                time: chrono::DateTime::from_timestamp_millis(t.time).unwrap_or_default(),
                is_buyer_maker: t.is_buyer_maker,
                side: if t.is_buyer_maker { Side::Sell } else { Side::Buy },
            })
            .collect())
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Side {
    Buy,
    Sell,
}

#[derive(Debug, Clone)]
pub struct Order {
    pub price: Decimal,
    pub amount: Decimal,
    pub total: Decimal,
    pub side: Side,
}

impl Order {
    pub fn new(price_str: String, amount_str: String, side: Side) -> Self {
        let price = price_str.parse::<Decimal>().unwrap_or_default();
        let amount = amount_str.parse::<Decimal>().unwrap_or_default();
        
        Self {
            price,
            amount,
            total: price * amount,
            side,
        }
    }
}

impl Ord for Order {
    fn cmp(&self, other: &Self) -> Ordering {
        match self.side {
            Side::Buy => other.price.cmp(&self.price),  // Sort bids in descending order
            Side::Sell => self.price.cmp(&other.price), // Sort asks in ascending order
        }
    }
}

impl PartialOrd for Order {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl PartialEq for Order {
    fn eq(&self, other: &Self) -> bool {
        self.price == other.price
    }
}

impl Eq for Order {}

#[derive(Debug, Clone)]
pub struct OrderBook {
    pub bids: Vec<Order>,
    pub asks: Vec<Order>,
}

#[derive(Debug, Clone)]
pub struct Ticker {
    pub last_price: Decimal,
    pub open_price: Decimal,
    pub high_price: Decimal,
    pub low_price: Decimal,
    pub volume: Decimal,
    pub price_change_percent: Decimal,
}

#[derive(Debug, Clone)]
pub struct Trade {
    pub id: u64,
    pub price: Decimal,
    pub qty: Decimal,
    pub time: DateTime<Utc>,
    pub is_buyer_maker: bool,
    pub side: Side,
}

#[derive(Deserialize, Debug)]
struct OrderBookResponse {
    bids: Vec<[String; 2]>,
    asks: Vec<[String; 2]>,
}

#[derive(Deserialize, Debug)]
struct TickerResponse {
    #[serde(rename = "lastPrice")]
    last_price: Decimal,
    #[serde(rename = "openPrice")]
    open_price: Decimal,
    #[serde(rename = "highPrice")]
    high_price: Decimal,
    #[serde(rename = "lowPrice")]
    low_price: Decimal,
    #[serde(rename = "volume")]
    volume: Decimal,
    #[serde(rename = "priceChangePercent")]
    price_change_percent: Decimal,
}

#[derive(Deserialize, Debug)]
struct TradeResponse {
    id: u64,
    price: Decimal,
    #[serde(rename = "qty")]
    qty: Decimal,
    time: i64,
    #[serde(rename = "isBuyerMaker")]
    is_buyer_maker: bool,
}