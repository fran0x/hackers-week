import ccxt
import pandas as pd
import numpy as np
import time
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Initialize the Binance client
exchange = ccxt.binance()

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
               style={'fontFamily': 'courier, monospace', 'fontSize': 16}),
        dbc.Row([
            dbc.Col([
                html.Div(id='market-info', className="text-center mb-3"),
            ], width=12)
        ]),
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
     Output('market-info', 'children')],
    Input('interval-component', 'n_intervals')
)
def update_data(n):
    try:
        # Fetch the order book data from Binance
        order_book = exchange.fetch_order_book('BTC/USDT', limit=10)
        
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
        
        # Process recent trades
        trades_data = []
        for trade in trades:
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
            
        # Define trades columns
        trades_columns = [
            {"name": "Time", "id": "time"},
            {"name": "Price (USDT)", "id": "price"},
            {"name": "Amount (BTC)", "id": "amount"},
            {"name": "Side", "id": "side"}  # Hidden column for coloring
        ]
        
        return combined_book.to_dict('records'), columns, trades_data, trades_columns, market_info
    
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
        
        return error_data, order_book_columns, trades_error_data, trades_columns, error_info

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)