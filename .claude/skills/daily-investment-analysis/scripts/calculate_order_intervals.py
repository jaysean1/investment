#!/usr/bin/env python3
# location: .claude/skills/daily-investment-analysis/scripts/calculate_order_intervals.py
# This script generates 3-tier layered limit orders based on price trends and market conditions
# Adjusts intervals based on market phase (downtrend/consolidation/uptrend)

import pandas as pd
import sys
from datetime import datetime

def detect_market_phase(recent_prices, current_price):
    """
    Detect market phase based on recent price action

    Args:
        recent_prices: List of recent closing prices (most recent last)
        current_price: Current price

    Returns:
        str: 'downtrend', 'consolidation', or 'uptrend'
    """
    if len(recent_prices) < 5:
        return 'consolidation'

    # Calculate simple moving average
    sma_5 = sum(recent_prices[-5:]) / 5
    sma_10 = sum(recent_prices[-10:]) / 10 if len(recent_prices) >= 10 else sma_5

    # Recent volatility
    recent_high = max(recent_prices[-5:])
    recent_low = min(recent_prices[-5:])
    volatility_pct = ((recent_high - recent_low) / recent_low) * 100

    # Trend detection
    if current_price < sma_5 * 0.97:  # 3% below 5-day average
        return 'downtrend'
    elif current_price > sma_5 * 1.03:  # 3% above 5-day average
        return 'uptrend'
    else:
        return 'consolidation'

def calculate_order_levels(symbol, current_price, market_phase, asset_type):
    """
    Calculate 3-tier order levels based on market conditions

    Args:
        symbol: Stock ticker
        current_price: Current market price
        market_phase: 'downtrend', 'consolidation', or 'uptrend'
        asset_type: 'core', 'rhythm', 'tactical', or 'defensive'

    Returns:
        list of dicts with 'price' and 'quantity' for each order level
    """
    orders = []

    # Base intervals by market phase
    if market_phase == 'downtrend':
        # Wider intervals during downtrends
        intervals = [-5, -10, -15]  # Percentage below current
        base_qty = 1
    elif market_phase == 'consolidation':
        # Tighter intervals during consolidation
        intervals = [-2, -4, -6]
        base_qty = 1
    else:  # uptrend
        # Minimal/no orders during uptrend (observation mode)
        return []  # No orders in strong uptrend

    # Adjust by asset type
    qty_multipliers = {
        'core': 1,      # MSFT - single shares
        'rhythm': 2,    # QQQ - more frequent, larger quantities
        'tactical': 1,  # TSLA - conservative
        'defensive': 1  # GLD - static holding
    }

    multiplier = qty_multipliers.get(asset_type, 1)

    # Generate orders
    for interval in intervals:
        order_price = current_price * (1 + interval / 100)
        # Round to nearest $1 for readability
        order_price = round(order_price)

        orders.append({
            'quantity': base_qty * multiplier,
            'price': order_price
        })

    return orders

def format_order_line(date, symbol, orders, operation='买入'):
    """
    Format order line for 04_order_log.md

    Returns:
        str: Formatted markdown table row
    """
    if not orders:
        return None

    # Format: "1 @ 505 / 1 @ 500 / 1 @ 495"
    order_str = ' / '.join([f"{o['quantity']} @ {o['price']}" for o in orders])

    return f"| {date} | {symbol}({operation}) | {order_str} |"

def generate_all_orders(date, prices_dict, csv_data_dict):
    """
    Generate orders for all 4 assets

    Args:
        date: Trading date string
        prices_dict: Dict with current prices {symbol: price}
        csv_data_dict: Dict with historical price data {symbol: dataframe}

    Returns:
        list of formatted order strings
    """
    asset_configs = {
        'MSFT': 'core',
        'QQQ': 'rhythm',
        'TSLA': 'tactical',
        'GLD': 'defensive'
    }

    all_orders = []

    for symbol, asset_type in asset_configs.items():
        if symbol not in prices_dict or symbol not in csv_data_dict:
            continue

        current_price = prices_dict[symbol]
        df = csv_data_dict[symbol]

        # Get recent prices for trend detection
        recent_prices = df['Close'].tail(10).tolist()

        # Detect market phase
        phase = detect_market_phase(recent_prices, current_price)

        # Calculate order levels
        orders = calculate_order_levels(symbol, current_price, phase, asset_type)

        # Format order line
        if orders:
            order_line = format_order_line(date, symbol, orders)
            if order_line:
                all_orders.append(order_line)

    return all_orders

if __name__ == '__main__':
    # Example usage
    if len(sys.argv) >= 3:
        symbol = sys.argv[1]
        current_price = float(sys.argv[2])
        market_phase = sys.argv[3] if len(sys.argv) > 3 else 'consolidation'
        asset_type = sys.argv[4] if len(sys.argv) > 4 else 'core'

        orders = calculate_order_levels(symbol, current_price, market_phase, asset_type)

        print(f"\n{symbol} Order Levels ({market_phase}):")
        print(f"Current Price: ${current_price:.2f}")
        print("\nSuggested Orders:")
        for i, order in enumerate(orders, 1):
            print(f"  Level {i}: {order['quantity']} @ ${order['price']}")
    else:
        print("Usage: python calculate_order_intervals.py SYMBOL CURRENT_PRICE [MARKET_PHASE] [ASSET_TYPE]")
        print("Example: python calculate_order_intervals.py MSFT 513.58 consolidation core")
