import ccxt
import pandas as pd
import numpy as np
import time
import uuid
import dash
from dash import dcc, html, dash_table, callback_context
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# Import the trader module
from trader import Trader, SimpleOrderBook, OrderType, OrderStatus, Order

# Initialize the Binance client
exchange = ccxt.binance()

# Initialize our trading system
simple_order_book = SimpleOrderBook(symbol="BTC/USDT")
trader = Trader(id="user", btc_balance=1.0, usdt_balance=50000.0)

# Store initial portfolio value to calculate PnL
try:
    initial_ticker = exchange.fetch_ticker('BTC/USDT')
    initial_btc_value = trader.balances['BTC'] * initial_ticker['last']
    initial_portfolio_value = trader.balances['USDT'] + initial_btc_value
except Exception:
    # Fallback if we can't get the ticker
    initial_portfolio_value = 51000.0  # Assume roughly 1 BTC = 50000 + 1000 USDT

# Define the application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Apply background color to the entire app
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: black;
                margin: 0;
                padding: 0;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''
app.title = "BTC/USDT Order Book"

# Define the layout
app.layout = html.Div(style={'backgroundColor': 'black'}, children=[
    dbc.Container(style={'backgroundColor': 'black'}, children=[
        html.H3("BTC/USDT", className="text-center my-3", 
               style={'fontFamily': 'courier, monospace', 'fontSize': 16, 'fontWeight': 'bold'}),
        
        # Market Information
        dbc.Row([
            dbc.Col([
                html.Div(id='market-info', className="text-center mb-3"),
            ], width=12)
        ]),
        
        # Trading Form
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3("MARKET ORDER", className="text-center my-3", 
                               style={'fontFamily': 'courier, monospace', 'fontSize': 16, 'fontWeight': 'bold'}),
                        
                        # Trader Balance - Moved inside the card
                        html.Div(id='trader-balance', className="text-center mb-3"),
                        
                        # Order tabs for Market and Limit orders
                        dbc.Tabs([
                            dbc.Tab(label="MARKET", tab_id="market-tab", 
                                   label_style={'fontWeight': 'bold', 'color': 'white'},
                                   active_label_style={'color': 'white'},
                                   children=[
                                # Market order form with buy/sell buttons
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Amount (BTC)", style={'fontFamily': 'courier, monospace', 'marginTop': '10px', 'fontSize': 12}),
                                        dbc.Input(id='market-amount', type='number', placeholder='Enter BTC amount', 
                                                 min=0.001, step=0.001, value=0.01),
                                    ], width=6),
                                    
                                    dbc.Col([
                                        dbc.Button("BUY", id='market-buy-btn', color="success", className="w-100",
                                                  style={'fontWeight': 'bold', 'marginTop': '35px'}),
                                    ], width=3),
                                    
                                    dbc.Col([
                                        dbc.Button("SELL", id='market-sell-btn', color="danger", className="w-100",
                                                  style={'fontWeight': 'bold', 'marginTop': '35px'}),
                                    ], width=3),
                                ], className="mb-2 align-items-center")
                            ]),
                            
                            dbc.Tab(label="LIMIT", tab_id="limit-tab", 
                                   label_style={'fontWeight': 'bold', 'color': 'white'},
                                   active_label_style={'color': 'white'},
                                   children=[
                                # Limit order form with price field and buy/sell buttons
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Amount (BTC)", style={'fontFamily': 'courier, monospace', 'marginTop': '10px', 'fontSize': 12}),
                                        dbc.Input(id='limit-amount', type='number', placeholder='BTC amount', 
                                                 min=0.001, step=0.001, value=0.01),
                                    ], width=4),
                                    
                                    dbc.Col([
                                        dbc.Label("Price (USDT)", style={'fontFamily': 'courier, monospace', 'marginTop': '10px', 'fontSize': 12}),
                                        dbc.Input(id='limit-price', type='number', placeholder='Limit price', 
                                                 min=0.01, step=0.01),
                                    ], width=4),
                                    
                                    dbc.Col([
                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Button("LIMIT BUY", id='limit-buy-btn', color="success", className="w-100",
                                                          style={'fontWeight': 'bold', 'marginTop': '35px', 'fontSize': 12}),
                                            ], width=6),
                                            
                                            dbc.Col([
                                                dbc.Button("LIMIT SELL", id='limit-sell-btn', color="danger", className="w-100",
                                                          style={'fontWeight': 'bold', 'marginTop': '35px', 'fontSize': 12}),
                                            ], width=6),
                                        ]),
                                    ], width=4),
                                ], className="mb-2 align-items-center")
                            ]),
                        ], id="order-tabs", active_tab="market-tab", className="mb-3"),
                        
                        # Hidden input to store order type (will be set by the buttons)
                        dcc.Store(id='order-type', data='buy')
                    ])
                ], style={'backgroundColor': 'black', 'borderColor': '#333'})
            ], width=12)
        ], className="mb-3"),
        
        # Toast for notifications
        html.Div(id='notification-container'),
        dbc.Row([
            # Order Book Column
            dbc.Col([
                html.H6("Order Book", className="text-center mb-2", 
                       style={'color': 'white', 'fontFamily': 'courier, monospace', 'fontSize': 14}),
                dash_table.DataTable(
                    id='order-book-table',
                    style_header={
                        'backgroundColor': '#30404D',
                        'color': 'white',
                        'fontWeight': 'bold',
                        'textAlign': 'center'
                    },
                    style_cell={
                        'backgroundColor': 'black',
                        'color': 'white',
                        'textAlign': 'center',
                        'font-family': 'courier, monospace',
                        'fontSize': 12,
                        'padding': '5px'
                    },
                    style_cell_conditional=[
                        {
                            'if': {'column_id': 'type'},
                            'display': 'none'
                        }
                    ],
                    style_data_conditional=[
                        # Asks (sell orders) - red
                        {
                            'if': {'filter_query': '{type} = "ask"'},
                            'backgroundColor': 'black'
                        },
                        {
                            'if': {'filter_query': '{type} = "ask"', 'column_id': 'price'},
                            'color': '#ff5c5c',
                            'fontWeight': 'bold'
                        },
                        # Bids (buy orders) - green
                        {
                            'if': {'filter_query': '{type} = "bid"'},
                            'backgroundColor': 'black'
                        },
                        {
                            'if': {'filter_query': '{type} = "bid"', 'column_id': 'price'},
                            'color': '#66ff66',
                            'fontWeight': 'bold'
                        },
                        # User's own ask orders - bright red background
                        {
                            'if': {'filter_query': '{type} = "user_ask"'},
                            'backgroundColor': '#3a1010'
                        },
                        {
                            'if': {'filter_query': '{type} = "user_ask"', 'column_id': 'price'},
                            'color': '#ff5c5c',
                            'fontWeight': 'bold'
                        },
                        # User's own bid orders - bright green background
                        {
                            'if': {'filter_query': '{type} = "user_bid"'},
                            'backgroundColor': '#103a10'
                        },
                        {
                            'if': {'filter_query': '{type} = "user_bid"', 'column_id': 'price'},
                            'color': '#66ff66',
                            'fontWeight': 'bold'
                        },
                        # Limit orders - with yellow highlighting
                        {
                            'if': {'filter_query': '{type} = "limit_ask"'},
                            'backgroundColor': '#3a1010',
                            'border': '1px solid yellow'
                        },
                        {
                            'if': {'filter_query': '{type} = "limit_ask"', 'column_id': 'price'},
                            'color': 'yellow',
                            'fontWeight': 'bold'
                        },
                        {
                            'if': {'filter_query': '{type} = "limit_bid"'},
                            'backgroundColor': '#103a10', 
                            'border': '1px solid yellow'
                        },
                        {
                            'if': {'filter_query': '{type} = "limit_bid"', 'column_id': 'price'},
                            'color': 'yellow',
                            'fontWeight': 'bold'
                        },
                        # Last price row - highlight
                        {
                            'if': {'filter_query': '{type} = "last"'},
                            'backgroundColor': 'black'
                        },
                        {
                            'if': {'filter_query': '{type} = "last"', 'column_id': 'price'},
                            'color': 'yellow',
                            'fontWeight': 'bold'
                        }
                    ]
                ),
            ], width=8),
            
            # Recent Trades Column
            dbc.Col([
                html.H6("Recent Trades", className="text-center mb-2", 
                       style={'color': 'white', 'fontFamily': 'courier, monospace', 'fontSize': 14}),
                dash_table.DataTable(
                    id='recent-trades-table',
                    style_header={
                        'backgroundColor': '#30404D',
                        'color': 'white',
                        'fontWeight': 'bold',
                        'textAlign': 'center'
                    },
                    style_cell={
                        'backgroundColor': 'black',
                        'color': 'white',
                        'textAlign': 'center',
                        'font-family': 'courier, monospace',
                        'fontSize': 12,
                        'padding': '5px'
                    },
                    style_data_conditional=[
                        # Buy trades - green
                        {
                            'if': {'filter_query': '{side} = "buy"', 'column_id': 'price'},
                            'color': '#66ff66',
                            'fontWeight': 'bold'
                        },
                        # Sell trades - red
                        {
                            'if': {'filter_query': '{side} = "sell"', 'column_id': 'price'},
                            'color': '#ff5c5c',
                            'fontWeight': 'bold'
                        }
                    ],
                    style_cell_conditional=[
                        {
                            'if': {'column_id': 'side'},
                            'display': 'none'
                        }
                    ]
                ),
            ], width=4),
            
            # Interval for data refresh
            dcc.Interval(
                id='interval-component',
                interval=2000,  # in milliseconds (2 seconds)
                n_intervals=0
            )
        ])
    ])
])

@app.callback(
    [Output('order-book-table', 'data'),
     Output('order-book-table', 'columns'),
     Output('recent-trades-table', 'data'),
     Output('recent-trades-table', 'columns'),
     Output('market-info', 'children'),
     Output('trader-balance', 'children')],
    Input('interval-component', 'n_intervals')
)
def update_data(n):
    try:
        # Fetch the order book data from Binance - 20 levels each side
        order_book = exchange.fetch_order_book('BTC/USDT', limit=20)
        
        # Fetch ticker for additional market info
        ticker = exchange.fetch_ticker('BTC/USDT')
        
        # Fetch recent trades
        trades = exchange.fetch_trades('BTC/USDT', limit=15)
        
        # Process bids and asks
        bids = pd.DataFrame(order_book['bids'], columns=['price', 'amount'])
        asks = pd.DataFrame(order_book['asks'], columns=['price', 'amount'])
        
        # Sort asks in descending order (highest ask at the top)
        asks = asks.sort_values('price', ascending=False)
        
        # Calculate total (price * amount) for each order
        bids['total'] = bids['price'] * bids['amount']
        asks['total'] = asks['price'] * asks['amount']
        
        # Add type column for styling
        asks['type'] = 'ask'
        bids['type'] = 'bid'
        
        # Add the trader's own active orders to the book display
        user_orders = []
        for order in simple_order_book.buy_orders + simple_order_book.sell_orders:
            if order.trader_id == trader.id and order.remaining_amount > 0:
                # Any trader orders in the book are limit orders
                if order.status == OrderStatus.PARTIALLY_FILLED:
                    # This is a partially filled limit order
                    user_type = 'limit_bid' if order.type == OrderType.BUY else 'limit_ask'
                else:
                    # This is a regular limit order
                    user_type = 'limit_bid' if order.type == OrderType.BUY else 'limit_ask'
                
                user_orders.append({
                    'price': order.price,
                    'amount': order.remaining_amount,
                    'total': order.price * order.remaining_amount,
                    'type': user_type
                })
        
        # Create DataFrame for user orders if any exist
        if user_orders:
            user_df = pd.DataFrame(user_orders)
            # Concatenate with market orders
            if not user_df.empty:
                # Add user orders to the appropriate side
                user_bids = user_df[user_df['type'] == 'user_bid'].copy()
                user_asks = user_df[user_df['type'] == 'user_ask'].copy()
                
                # Combine user orders with market orders
                if not user_bids.empty:
                    bids = pd.concat([bids, user_bids])
                    bids = bids.sort_values('price', ascending=False)
                
                if not user_asks.empty:
                    asks = pd.concat([asks, user_asks])
                    asks = asks.sort_values('price', ascending=False)
                
        # Create a single row for the last price
        last_price_row = pd.DataFrame([{
            'price': ticker['last'],
            'amount': '',  # Empty for the last price row
            'total': '',   # Empty for the last price row
            'type': 'last'
        }])
        
        # Format the data for display (after all calculations)
        asks['price'] = asks['price'].apply(lambda x: f"{x:,.2f}")
        bids['price'] = bids['price'].apply(lambda x: f"{x:,.2f}")
        last_price_row['price'] = last_price_row['price'].apply(lambda x: f"{x:,.2f}")
        
        asks['amount'] = asks['amount'].apply(lambda x: f"{x:,.6f}")
        bids['amount'] = bids['amount'].apply(lambda x: f"{x:,.6f}")
        
        asks['total'] = asks['total'].apply(lambda x: f"{x:,.2f}")
        bids['total'] = bids['total'].apply(lambda x: f"{x:,.2f}")
        
        # Combine into a single table
        combined_book = pd.concat([asks, last_price_row, bids])
        
        # Define table columns
        columns = [
            {"name": "Price (USDT)", "id": "price"},
            {"name": "Amount (BTC)", "id": "amount"},
            {"name": "Total (USDT)", "id": "total"},
            {"name": "Type", "id": "type"}  # Used for styling but still displayed
        ]
        
        # Calculate spread using raw data before string formatting
        ask_low = float(order_book['asks'][0][0])
        bid_high = float(order_book['bids'][0][0])
        spread = ask_low - bid_high
        
        # Get current time
        current_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Fetch additional OHLC data for the day
        try:
            # Get daily OHLC data (1d timeframe)
            ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1d', limit=1)
            daily_open = ohlcv[0][1]  # The open price from the daily candle
            daily_high = ohlcv[0][2]  # The high price from the daily candle
            daily_low = ohlcv[0][3]   # The low price from the daily candle
        except Exception:
            # Fallback to ticker data if OHLCV fetch fails
            daily_open = ticker['open']
            daily_high = ticker['high']
            daily_low = ticker['low']
        
        # Create market info display
        market_info = [
            html.Div([
                html.Span(f"O: {daily_open:,.2f} | "),
                html.Span(f"H: {daily_high:,.2f} | "),
                html.Span(f"L: {daily_low:,.2f} | "),
                html.Span(f"C: {ticker['last']:,.2f}")
            ], className="mb-2", style={'fontFamily': 'courier, monospace', 'fontSize': 12}),
            html.Div([
                html.Span(f"24h Volume: {ticker['baseVolume']:,.2f} BTC | "),
                html.Span(f"Spread: {spread:,.2f} | "),
                html.Span(f"24h Change: {ticker['percentage']:.2f}%")
            ], style={'fontFamily': 'courier, monospace', 'fontSize': 12}),
            html.Div([
                html.Span(f"Time: {current_time}", style={'color': '#999999'})
            ], className="mt-2", style={'fontFamily': 'courier, monospace', 'fontSize': 12})
        ]
        
        # Calculate total USD value including BTC
        btc_value_in_usdt = trader.balances['BTC'] * ticker['last']
        total_value = trader.balances['USDT'] + btc_value_in_usdt
        
        # Calculate PnL percentage
        pnl_percent = ((total_value - initial_portfolio_value) / initial_portfolio_value) * 100
        
        # Determine color for PnL
        if pnl_percent > 0:
            pnl_color = '#66ff66'  # Green for profit
            pnl_prefix = '+'
        elif pnl_percent < 0:
            pnl_color = '#ff5c5c'  # Red for loss
            pnl_prefix = ''
        else:
            pnl_color = 'yellow'   # Yellow for no change
            pnl_prefix = ''
        
        # Create trader balance display with same style as market info
        trader_balance = html.Div([
            html.Div([
                html.Span(f"BTC: {trader.balances['BTC']:,.6f} | ", 
                          style={'color': '#66ff66'}),
                html.Span(f"USDT: {trader.balances['USDT']:,.2f} | ",
                          style={'color': '#ff5c5c'}),
                html.Span(f"Total Value: ", style={}),
                html.Span(f"{total_value:,.2f} USDT ", 
                          style={'color': 'yellow', 'fontWeight': 'bold'}),
                html.Span(f"({pnl_prefix}{pnl_percent:.2f}%)", 
                          style={'color': pnl_color, 'fontWeight': 'bold', 'marginLeft': '5px'})
            ], className="mb-2", style={'fontFamily': 'courier, monospace', 'fontSize': 12})
        ])
        
        # Market price info has been removed
        
        # Process recent trades
        trades_data = []
        
        # First add trader's own trades
        for trade in trader.trades[-10:]:  # Show the most recent 10 trader trades
            timestamp = time.strftime('%H:%M:%S', time.localtime(trade.timestamp))
            side = "buy" if trade.type == OrderType.BUY else "sell"
            price = f"{trade.price:,.2f}"
            amount = f"{trade.amount:,.6f}"
            
            trades_data.append({
                'time': timestamp,
                'price': price,
                'amount': amount,
                'side': side
            })
        
        # Then add market trades (if there's room)
        max_trades = 15
        remaining_slots = max_trades - len(trades_data)
        
        if remaining_slots > 0:
            for trade in trades[:remaining_slots]:
                timestamp = pd.to_datetime(trade['timestamp'], unit='ms').strftime('%H:%M:%S')
                side = trade['side']  # 'buy' or 'sell'
                price = f"{trade['price']:,.2f}"
                amount = f"{trade['amount']:,.6f}"
                
                trades_data.append({
                    'time': timestamp,
                    'price': price,
                    'amount': amount,
                    'side': side
                })
        
        # Sort trades by time (most recent first)
        trades_data = sorted(trades_data, key=lambda x: x['time'], reverse=True)
            
        # Define trades columns
        trades_columns = [
            {"name": "Time", "id": "time"},
            {"name": "Price (USDT)", "id": "price"},
            {"name": "Amount (BTC)", "id": "amount"},
            {"name": "Side", "id": "side"}  # Hidden column for coloring
        ]
        
        return combined_book.to_dict('records'), columns, trades_data, trades_columns, market_info, trader_balance
    
    except Exception as e:
        # Handle errors gracefully
        print(f"Error fetching data: {e}")
        
        # Create empty tables with the correct structure
        order_book_columns = [
            {"name": "Price (USDT)", "id": "price"},
            {"name": "Amount (BTC)", "id": "amount"},
            {"name": "Total (USDT)", "id": "total"},
            {"name": "Type", "id": "type"}
        ]
        
        trades_columns = [
            {"name": "Time", "id": "time"},
            {"name": "Price (USDT)", "id": "price"},
            {"name": "Amount (BTC)", "id": "amount"},
            {"name": "Side", "id": "side"}
        ]
        
        error_data = [{'price': 'Error fetching data', 'amount': '', 'total': '', 'type': 'last'}]
        trades_error_data = [{'time': 'Error', 'price': '', 'amount': '', 'side': ''}]
        error_info = [html.Div(f"Error fetching data: {str(e)}", style={'color': 'red'})]
        empty_trader_balance = html.Div("Error loading trader balances", style={'color': 'red'})
        return error_data, order_book_columns, trades_error_data, trades_columns, error_info, empty_trader_balance

# Handle market order placement based on which button is clicked
@app.callback(
    [Output('notification-container', 'children'),
     Output('order-type', 'data')],
    [Input('market-buy-btn', 'n_clicks'),
     Input('market-sell-btn', 'n_clicks')],
    [State('order-type', 'data'),
     State('market-amount', 'value')],
    prevent_initial_call=True
)
def place_market_order(buy_clicks, sell_clicks, current_order_type, amount):
    # Determine which button was clicked
    ctx = callback_context
    if not ctx.triggered:
        return [dash.no_update, current_order_type]
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'market-buy-btn':
        order_type = 'buy'
    elif button_id == 'market-sell-btn':
        order_type = 'sell'
    else:
        return [dash.no_update, current_order_type]
    
    if amount is None:
        return [dash.no_update, order_type]
    
    try:
        # Get the current market price
        ticker = exchange.fetch_ticker('BTC/USDT')
        current_price = ticker['last']
        
        # For market orders, get the best price from Binance
        binance_order_book = exchange.fetch_order_book('BTC/USDT', limit=1)
        
        # Create a market counterparty for the trade
        counterparty_id = str(uuid.uuid4())
        
        if order_type == 'buy':
            # For buy orders, we match with the lowest ask in the market
            if not binance_order_book['asks'] or len(binance_order_book['asks']) == 0:
                notification = dbc.Toast(
                    "No sell orders available in the market.",
                    id="order-notification",
                    header="Market Order Failed",
                    icon="danger",
                    dismissable=True,
                    is_open=True,
                    duration=4000,
                    style={"position": "fixed", "top": 10, "right": 10, "width": 350, 
                           "backgroundColor": "#d9534f", "color": "white", "zIndex": 1000}
                )
                return [notification]
            
            # Get the best ask price (lowest selling price)
            best_ask = binance_order_book['asks'][0]
            market_price = float(best_ask[0])
            available_amount = float(best_ask[1])
            
            # Create a market sell order to match with our buy
            market_order = Order(
                id=counterparty_id,
                trader_id="market",
                type=OrderType.SELL,
                symbol="BTC/USDT",
                amount=available_amount,
                price=market_price,
                timestamp=time.time(),
                status=OrderStatus.PENDING
            )
            
            # Clear any old orders
            simple_order_book.sell_orders = [market_order]
            
            # Execute the buy order (which can be partially filled)
            executed_trades = trader.place_market_buy_order(simple_order_book, amount, market_price)
            
            # Clear the market order from the order book after execution
            simple_order_book.sell_orders = []
            
        else:  # Sell order
            # For sell orders, we match with the highest bid in the market
            if not binance_order_book['bids'] or len(binance_order_book['bids']) == 0:
                notification = dbc.Toast(
                    "No buy orders available in the market.",
                    id="order-notification",
                    header="Market Order Failed",
                    icon="danger",
                    dismissable=True,
                    is_open=True,
                    duration=4000,
                    style={"position": "fixed", "top": 10, "right": 10, "width": 350, 
                           "backgroundColor": "#d9534f", "color": "white", "zIndex": 1000}
                )
                return [notification]
            
            # Get the best bid price (highest buying price)
            best_bid = binance_order_book['bids'][0]
            market_price = float(best_bid[0])
            available_amount = float(best_bid[1])
            
            # Create a market buy order to match with our sell
            market_order = Order(
                id=counterparty_id,
                trader_id="market",
                type=OrderType.BUY,
                symbol="BTC/USDT",
                amount=available_amount,
                price=market_price,
                timestamp=time.time(),
                status=OrderStatus.PENDING
            )
            
            # Clear any old orders
            simple_order_book.buy_orders = [market_order]
            
            # Execute the sell order (which can be partially filled)
            executed_trades = trader.place_market_sell_order(simple_order_book, amount, market_price)
            
            # Clear the market order from the order book after execution
            simple_order_book.buy_orders = []
        
        # Generate notification based on the result
        if executed_trades and len(executed_trades) > 0:
            total_amount = sum(trade.amount for trade in executed_trades)
            
            # Avoid division by zero
            if total_amount > 0:
                avg_price = sum(trade.price * trade.amount for trade in executed_trades) / total_amount
            else:
                avg_price = market_price
            
            # Check if it was a partial fill
            is_partial = total_amount < amount
            fill_status = "Partially" if is_partial else "Fully"
            
            notification = dbc.Toast(
                [
                    html.P(f"Market order {fill_status.lower()} executed!"),
                    html.P(f"Filled: {total_amount:.6f} BTC at price: {avg_price:.2f} USDT"),
                    html.P(f"Total value: {total_amount * avg_price:.2f} USDT"),
                    html.P(f"Requested: {amount:.6f} BTC", style={'opacity': '0.8'}) if is_partial else None
                ],
                id="order-notification",
                header=f"{fill_status} Filled {order_type.capitalize()}",
                icon="success",
                dismissable=True,
                is_open=True,
                duration=5000,
                style={"position": "fixed", "top": 10, "right": 10, "width": 350, 
                       "backgroundColor": "#3a4d56", "color": "white", "zIndex": 1000}
            )
            return [notification, order_type]
        else:
            # Order failed or couldn't be matched
            notification = dbc.Toast(
                "Market order could not be executed. Check your balance and try again.",
                id="order-notification",
                header="Market Order Failed",
                icon="danger",
                dismissable=True,
                is_open=True,
                duration=4000,
                style={"position": "fixed", "top": 10, "right": 10, "width": 350, 
                       "backgroundColor": "#d9534f", "color": "white", "zIndex": 1000}
            )
            return [notification, order_type]
    
    except Exception as e:
        # Handle errors
        notification = dbc.Toast(
            str(e),
            id="order-notification",
            header="Error",
            icon="danger",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350, 
                   "backgroundColor": "#d9534f", "color": "white", "zIndex": 1000}
        )
        return [notification, order_type]

# Handle limit order placement
@app.callback(
    [Output('notification-container', 'children', allow_duplicate=True),
     Output('order-type', 'data', allow_duplicate=True)],
    [Input('limit-buy-btn', 'n_clicks'),
     Input('limit-sell-btn', 'n_clicks')],
    [State('order-type', 'data'),
     State('limit-amount', 'value'),
     State('limit-price', 'value')],
    prevent_initial_call=True
)
def place_limit_order(buy_clicks, sell_clicks, current_order_type, amount, price):
    # Determine which button was clicked
    ctx = callback_context
    if not ctx.triggered:
        return [dash.no_update, current_order_type]
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'limit-buy-btn':
        order_type = 'buy'
    elif button_id == 'limit-sell-btn':
        order_type = 'sell'
    else:
        return [dash.no_update, current_order_type]
    
    if amount is None or price is None:
        notification = dbc.Toast(
            "Please specify both amount and price for limit orders.",
            id="order-notification",
            header="Limit Order Error",
            icon="danger",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350, 
                   "backgroundColor": "#d9534f", "color": "white", "zIndex": 1000}
        )
        return [notification, order_type]
    
    try:
        # Get the current market order book for reference
        binance_order_book = exchange.fetch_order_book('BTC/USDT', limit=1)
        
        # Place the limit order using the proper trader method
        if order_type == 'buy':
            executed_trades = trader.place_limit_buy_order(simple_order_book, amount, price)
            
            # Check result and show appropriate notification
            if executed_trades and len(executed_trades) > 0:
                # Order executed (fully or partially)
                total_amount = sum(trade.amount for trade in executed_trades)
                
                # Calculate average execution price
                if total_amount > 0:
                    avg_price = sum(trade.price * trade.amount for trade in executed_trades) / total_amount
                else:
                    # This shouldn't happen if we have trades, but just in case
                    avg_price = price
                
                # Check if fully executed by comparing with original amount
                if total_amount < amount:
                    # Partially executed
                    remaining_amount = amount - total_amount
                    
                    notification = dbc.Toast(
                        [
                            html.P(f"Limit Buy Order partially executed immediately:"),
                            html.P(f"Executed: {total_amount:.6f} BTC at {avg_price:.2f} USDT"),
                            html.P(f"Remaining: {remaining_amount:.6f} BTC at {price:.2f} USDT placed in order book")
                        ],
                        id="order-notification",
                        header="Limit Buy Partially Executed",
                        icon="success",
                        dismissable=True,
                        is_open=True,
                        duration=5000,
                        style={"position": "fixed", "top": 10, "right": 10, "width": 350, 
                              "backgroundColor": "#3a4d56", "color": "white", "zIndex": 1000}
                    )
                else:
                    # Fully executed immediately
                    notification = dbc.Toast(
                        [
                            html.P(f"Limit Buy Order executed immediately:"),
                            html.P(f"Executed: {total_amount:.6f} BTC at {avg_price:.2f} USDT")
                        ],
                        id="order-notification",
                        header="Limit Buy Executed",
                        icon="success",
                        dismissable=True,
                        is_open=True,
                        duration=4000,
                        style={"position": "fixed", "top": 10, "right": 10, "width": 350, 
                              "backgroundColor": "#3a4d56", "color": "white", "zIndex": 1000}
                    )
            else:
                # Not executed - just placed in the order book
                notification = dbc.Toast(
                    f"Limit Buy Order placed for {amount:.6f} BTC at {price:.2f} USDT",
                    id="order-notification",
                    header="Limit Buy Order Placed",
                    icon="success",
                    dismissable=True,
                    is_open=True,
                    duration=4000,
                    style={"position": "fixed", "top": 10, "right": 10, "width": 350, 
                          "backgroundColor": "#3a4d56", "color": "white", "zIndex": 1000}
                )
                
        else:  # Sell order
            executed_trades = trader.place_limit_sell_order(simple_order_book, amount, price)
            
            # Check result and show appropriate notification
            if executed_trades and len(executed_trades) > 0:
                # Order executed (fully or partially)
                total_amount = sum(trade.amount for trade in executed_trades)
                
                # Calculate average execution price
                if total_amount > 0:
                    avg_price = sum(trade.price * trade.amount for trade in executed_trades) / total_amount
                else:
                    # Fallback (shouldn't happen)
                    avg_price = price
                
                # Check if fully executed by comparing with original amount
                if total_amount < amount:
                    # Partially executed
                    remaining_amount = amount - total_amount
                    
                    notification = dbc.Toast(
                        [
                            html.P(f"Limit Sell Order partially executed immediately:"),
                            html.P(f"Executed: {total_amount:.6f} BTC at {avg_price:.2f} USDT"),
                            html.P(f"Remaining: {remaining_amount:.6f} BTC at {price:.2f} USDT placed in order book")
                        ],
                        id="order-notification",
                        header="Limit Sell Partially Executed",
                        icon="success",
                        dismissable=True,
                        is_open=True,
                        duration=5000,
                        style={"position": "fixed", "top": 10, "right": 10, "width": 350, 
                              "backgroundColor": "#3a4d56", "color": "white", "zIndex": 1000}
                    )
                else:
                    # Fully executed immediately
                    notification = dbc.Toast(
                        [
                            html.P(f"Limit Sell Order executed immediately:"),
                            html.P(f"Executed: {total_amount:.6f} BTC at {avg_price:.2f} USDT")
                        ],
                        id="order-notification",
                        header="Limit Sell Executed",
                        icon="success",
                        dismissable=True,
                        is_open=True,
                        duration=4000,
                        style={"position": "fixed", "top": 10, "right": 10, "width": 350, 
                              "backgroundColor": "#3a4d56", "color": "white", "zIndex": 1000}
                    )
            else:
                # Not executed - just placed in the order book
                notification = dbc.Toast(
                    f"Limit Sell Order placed for {amount:.6f} BTC at {price:.2f} USDT",
                    id="order-notification",
                    header="Limit Sell Order Placed",
                    icon="success",
                    dismissable=True,
                    is_open=True,
                    duration=4000,
                    style={"position": "fixed", "top": 10, "right": 10, "width": 350, 
                          "backgroundColor": "#3a4d56", "color": "white", "zIndex": 1000}
                )
        
        return [notification, order_type]
    
    except Exception as e:
        # Handle errors
        notification = dbc.Toast(
            str(e),
            id="order-notification",
            header="Limit Order Error",
            icon="danger",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350, 
                  "backgroundColor": "#d9534f", "color": "white", "zIndex": 1000}
        )
        return [notification, order_type]

# Add callback to autofill limit price with current market price
@app.callback(
    Output('limit-price', 'value'),
    [Input('order-tabs', 'active_tab')],
    prevent_initial_call=True
)
def update_limit_price(active_tab):
    if active_tab == "limit-tab":
        try:
            # Get current market price
            ticker = exchange.fetch_ticker('BTC/USDT')
            return ticker['last']
        except Exception:
            return None
    return dash.no_update

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)