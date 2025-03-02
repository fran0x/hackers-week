use crate::app::App;
use crate::binance::{Side, SYMBOL};
use ratatui::{
    layout::{Alignment, Constraint, Direction, Layout, Rect},
    style::{Color, Modifier, Style},
    widgets::{Block, Borders, Cell, Paragraph, Row, Table},
    Frame,
};

pub fn render(f: &mut Frame, app: &App) {
    // Create the layout
    let main_chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3), // Title
            Constraint::Length(4), // Market info
            Constraint::Min(10),   // Main content
            Constraint::Length(3), // Status bar
        ])
        .split(f.area());

    render_title(f, main_chunks[0]);
    render_market_info(f, main_chunks[1], app);

    // Split the main content into order book and recent trades
    let content_chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Percentage(70), // Order book
            Constraint::Percentage(30), // Recent trades
        ])
        .split(main_chunks[2]);

    render_order_book(f, content_chunks[0], app);
    render_recent_trades(f, content_chunks[1], app);
    render_status_bar(f, main_chunks[3], app);
}

fn render_title(f: &mut Frame, area: Rect) {
    let title = Paragraph::new(format!("{} Order Book", SYMBOL))
        .style(Style::default().fg(Color::Yellow))
        .alignment(Alignment::Center)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .style(Style::default().fg(Color::White))
                .border_style(Style::default().fg(Color::White)),
        );
    f.render_widget(title, area);
}

fn render_market_info(f: &mut Frame, area: Rect, app: &App) {
    let market_info_text = if let Some(ticker) = &app.ticker {
        let spread = match app.calculate_spread() {
            Some(spread) => format!("{:.2}", spread),
            None => "N/A".to_string(),
        };

        // Create a simple formatted text with the market information
        format!(
            "O: {:.2}  H: {:.2}  L: {:.2}  C: {:.2}\n\
             24h Volume: {:.2} BTC  |  Spread: {}  |  24h Change: {:.2}%",
            ticker.open_price,
            ticker.high_price,
            ticker.low_price,
            ticker.last_price,
            ticker.volume,
            spread,
            ticker.price_change_percent
        )
    } else {
        "Loading market data...".to_string()
    };

    let market_info = Paragraph::new(market_info_text)
        .alignment(Alignment::Center)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .title(" Market Information ")
                .border_style(Style::default().fg(Color::White)),
        );

    f.render_widget(market_info, area);
}

fn render_order_book(f: &mut Frame, area: Rect, app: &App) {
    let header_cells = ["Price (USDT)", "Amount (BTC)", "Total (USDT)"]
        .iter()
        .map(|h| Cell::from(*h).style(Style::default().fg(Color::Yellow)));
    let header = Row::new(header_cells).height(1).bottom_margin(1);

    let rows = if let Some(order_book) = &app.order_book {
        // Determine how many rows we have space for
        let available_rows = area.height.saturating_sub(4) as usize; // Account for header and borders
        let asks_rows = available_rows / 2;
        let bids_rows = available_rows - asks_rows;

        // Sort and limit asks and bids
        let mut sorted_asks = order_book.asks.clone();
        sorted_asks.sort_by(|a, b| b.price.cmp(&a.price)); // Highest asks first
        let asks_to_show = sorted_asks.iter().take(asks_rows);

        let mut sorted_bids = order_book.bids.clone();
        sorted_bids.sort_by(|a, b| b.price.cmp(&a.price)); // Highest bids first
        let bids_to_show = sorted_bids.iter().take(bids_rows);

        // Convert to rows
        let mut rows = Vec::new();

        // Add asks (sell orders) - in red
        for ask in asks_to_show {
            rows.push(Row::new(vec![
                Cell::from(format!("{:.2}", ask.price)).style(Style::default().fg(Color::Red)),
                Cell::from(format!("{:.6}", ask.amount)),
                Cell::from(format!("{:.2}", ask.total)),
            ]));
        }

        // Add current price row if available
        if let Some(ticker) = &app.ticker {
            rows.push(Row::new(vec![
                Cell::from(format!("{:.2}", ticker.last_price)).style(
                    Style::default()
                        .fg(Color::Yellow)
                        .add_modifier(Modifier::BOLD),
                ),
                Cell::from(""),
                Cell::from(""),
            ]));
        }

        // Add bids (buy orders) - in green
        for bid in bids_to_show {
            rows.push(Row::new(vec![
                Cell::from(format!("{:.2}", bid.price)).style(Style::default().fg(Color::Green)),
                Cell::from(format!("{:.6}", bid.amount)),
                Cell::from(format!("{:.2}", bid.total)),
            ]));
        }

        rows
    } else {
        vec![Row::new(vec![
            Cell::from("Loading order book..."),
            Cell::from(""),
            Cell::from(""),
        ])]
    };
    let widths = [
        Constraint::Percentage(33),
        Constraint::Percentage(33),
        Constraint::Percentage(34),
    ];

    let order_book_table = Table::new(rows, widths)
        .header(header)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .title(" Order Book ")
                .border_style(Style::default().fg(Color::White)),
        )
        .column_spacing(1);

    f.render_widget(order_book_table, area);
}

fn render_recent_trades(f: &mut Frame, area: Rect, app: &App) {
    let header_cells = ["Time", "Price", "Amount"]
        .iter()
        .map(|h| Cell::from(*h).style(Style::default().fg(Color::Yellow)));
    let header = Row::new(header_cells).height(1).bottom_margin(1);

    let rows = if !app.trades.is_empty() {
        app.trades
            .iter()
            .map(|trade| {
                let price_color = match trade.side {
                    Side::Buy => Color::Green,
                    Side::Sell => Color::Red,
                };
                Row::new(vec![
                    Cell::from(trade.time.format("%H:%M:%S").to_string()),
                    Cell::from(format!("{:.2}", trade.price))
                        .style(Style::default().fg(price_color)),
                    Cell::from(format!("{:.6}", trade.qty)),
                ])
            })
            .collect()
    } else {
        vec![Row::new(vec![
            Cell::from("Loading trades..."),
            Cell::from(""),
            Cell::from(""),
        ])]
    };
    let widths = [
        Constraint::Percentage(30),
        Constraint::Percentage(35),
        Constraint::Percentage(35),
    ];

    let trades_table = Table::new(rows, widths)
        .header(header)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .title(" Recent Trades ")
                .border_style(Style::default().fg(Color::White)),
        )
        .column_spacing(1);

    f.render_widget(trades_table, area);
}

fn render_status_bar(f: &mut Frame, area: Rect, app: &App) {
    let status_text = match &app.error {
        Some(err) => format!("ERROR: {}", err),
        None => format!("{} - Press 'q' to quit, 'r' to refresh", app.status_message),
    };

    let status_bar = Paragraph::new(status_text)
        .alignment(Alignment::Left)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .border_style(Style::default().fg(Color::White)),
        );

    f.render_widget(status_bar, area);
}
