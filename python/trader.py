import time
import uuid
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class OrderType(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"

@dataclass
class Order:
    id: str
    trader_id: str
    type: OrderType
    symbol: str
    amount: float
    price: float
    timestamp: float
    status: OrderStatus
    filled_amount: float = 0
    remaining_amount: float = 0
    
    def __post_init__(self):
        if self.remaining_amount == 0:
            self.remaining_amount = self.amount

@dataclass
class Trade:
    id: str
    order_id: str
    trader_id: str
    symbol: str
    type: OrderType
    amount: float
    price: float
    timestamp: float
    total: float = 0
    
    def __post_init__(self):
        if self.total == 0:
            self.total = self.amount * self.price

class SimpleOrderBook:
    def __init__(self, symbol: str = "BTC/USDT"):
        self.symbol = symbol
        self.buy_orders: List[Order] = []
        self.sell_orders: List[Order] = []
        self.executed_trades: List[Trade] = []
    
    def add_order(self, order: Order) -> Optional[List[Trade]]:
        if order.type == OrderType.BUY:
            self.buy_orders.append(order)
            self.buy_orders.sort(key=lambda x: x.price, reverse=True)  # Sort by highest price first
            return self._match_buy_order(order)
        else:
            self.sell_orders.append(order)
            self.sell_orders.sort(key=lambda x: x.price)  # Sort by lowest price first
            return self._match_sell_order(order)
    
    def _match_buy_order(self, order: Order) -> Optional[List[Trade]]:
        executed_trades = []
        
        # Check if we can match this buy order with any sell orders
        for sell_order in self.sell_orders[:]:
            if sell_order.price > order.price:
                # Sell price is higher than buy price, no match
                continue
            
            # Calculate the matched amount
            matched_amount = min(order.remaining_amount, sell_order.remaining_amount)
            
            # Create a trade
            trade = Trade(
                id=str(uuid.uuid4()),
                order_id=order.id,
                trader_id=order.trader_id,
                symbol=self.symbol,
                type=order.type,
                amount=matched_amount,
                price=sell_order.price,  # Use the sell order price
                timestamp=time.time()
            )
            
            # Update the orders
            order.filled_amount += matched_amount
            order.remaining_amount -= matched_amount
            sell_order.filled_amount += matched_amount
            sell_order.remaining_amount -= matched_amount
            
            # Update order status
            if order.remaining_amount <= 0:
                order.status = OrderStatus.FILLED
            else:
                order.status = OrderStatus.PARTIALLY_FILLED
                
            if sell_order.remaining_amount <= 0:
                sell_order.status = OrderStatus.FILLED
                self.sell_orders.remove(sell_order)
            else:
                sell_order.status = OrderStatus.PARTIALLY_FILLED
            
            # Add trade to history
            executed_trades.append(trade)
            self.executed_trades.append(trade)
            
            # If the buy order is filled, stop matching
            if order.status == OrderStatus.FILLED:
                break
        
        return executed_trades if executed_trades else None
    
    def _match_sell_order(self, order: Order) -> Optional[List[Trade]]:
        executed_trades = []
        
        # Check if we can match this sell order with any buy orders
        for buy_order in self.buy_orders[:]:
            if buy_order.price < order.price:
                # Buy price is lower than sell price, no match
                continue
            
            # Calculate the matched amount
            matched_amount = min(order.remaining_amount, buy_order.remaining_amount)
            
            # Create a trade
            trade = Trade(
                id=str(uuid.uuid4()),
                order_id=order.id,
                trader_id=order.trader_id,
                symbol=self.symbol,
                type=order.type,
                amount=matched_amount,
                price=buy_order.price,  # Use the buy order price
                timestamp=time.time()
            )
            
            # Update the orders
            order.filled_amount += matched_amount
            order.remaining_amount -= matched_amount
            buy_order.filled_amount += matched_amount
            buy_order.remaining_amount -= matched_amount
            
            # Update order status
            if order.remaining_amount <= 0:
                order.status = OrderStatus.FILLED
            else:
                order.status = OrderStatus.PARTIALLY_FILLED
                
            if buy_order.remaining_amount <= 0:
                buy_order.status = OrderStatus.FILLED
                self.buy_orders.remove(buy_order)
            else:
                buy_order.status = OrderStatus.PARTIALLY_FILLED
            
            # Add trade to history
            executed_trades.append(trade)
            self.executed_trades.append(trade)
            
            # If the sell order is filled, stop matching
            if order.status == OrderStatus.FILLED:
                break
        
        return executed_trades if executed_trades else None

class Trader:
    def __init__(self, id: str, btc_balance: float = 1.0, usdt_balance: float = 10000.0):
        self.id = id
        self.balances = {
            "BTC": btc_balance,
            "USDT": usdt_balance
        }
        self.orders: List[Order] = []
        self.trades: List[Trade] = []
    
    def place_market_buy_order(self, order_book: SimpleOrderBook, amount: float, price: float) -> Optional[List[Trade]]:
        # Check if we have enough USDT
        cost = amount * price
        if self.balances["USDT"] < cost:
            print(f"Insufficient USDT balance. Required: {cost}, Available: {self.balances['USDT']}")
            return None
        
        # Create a new buy order
        order = Order(
            id=str(uuid.uuid4()),
            trader_id=self.id,
            type=OrderType.BUY,
            symbol=order_book.symbol,
            amount=amount,
            price=price,
            timestamp=time.time(),
            status=OrderStatus.PENDING
        )
        
        # Add the order to our records
        self.orders.append(order)
        
        # Add the order to the order book and get executed trades
        executed_trades = order_book.add_order(order)
        
        if executed_trades:
            # Update balances based on executed trades
            for trade in executed_trades:
                self.balances["BTC"] += trade.amount
                self.balances["USDT"] -= trade.total
                self.trades.append(trade)
            
            return executed_trades
        
        return None
    
    def place_market_sell_order(self, order_book: SimpleOrderBook, amount: float, price: float) -> Optional[List[Trade]]:
        # Check if we have enough BTC
        if self.balances["BTC"] < amount:
            print(f"Insufficient BTC balance. Required: {amount}, Available: {self.balances['BTC']}")
            return None
        
        # Create a new sell order
        order = Order(
            id=str(uuid.uuid4()),
            trader_id=self.id,
            type=OrderType.SELL,
            symbol=order_book.symbol,
            amount=amount,
            price=price,
            timestamp=time.time(),
            status=OrderStatus.PENDING
        )
        
        # Add the order to our records
        self.orders.append(order)
        
        # Add the order to the order book and get executed trades
        executed_trades = order_book.add_order(order)
        
        if executed_trades:
            # Update balances based on executed trades
            for trade in executed_trades:
                self.balances["BTC"] -= trade.amount
                self.balances["USDT"] += trade.total
                self.trades.append(trade)
            
            return executed_trades
        
        return None

# Example usage:
if __name__ == "__main__":
    # Create an order book
    order_book = SimpleOrderBook()
    
    # Create a trader
    trader = Trader(id="trader1", btc_balance=1.0, usdt_balance=30000.0)
    
    # Place buy and sell orders
    print(f"Initial BTC: {trader.balances['BTC']}, USDT: {trader.balances['USDT']}")
    
    # Buy BTC
    trades = trader.place_market_buy_order(order_book, amount=0.1, price=20000.0)
    if trades:
        print(f"Buy order executed! Trades: {len(trades)}")
    print(f"After buy - BTC: {trader.balances['BTC']}, USDT: {trader.balances['USDT']}")
    
    # Sell BTC
    trades = trader.place_market_sell_order(order_book, amount=0.05, price=21000.0)
    if trades:
        print(f"Sell order executed! Trades: {len(trades)}")
    print(f"After sell - BTC: {trader.balances['BTC']}, USDT: {trader.balances['USDT']}")