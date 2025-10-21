#!/usr/bin/env python3
# location: .claude/skills/daily-investment-analysis/scripts/update_holdings.py
# This script calculates weighted average cost basis and updates holdings
# Processes transaction history to maintain accurate position tracking

import pandas as pd
import sys
from collections import defaultdict

def calculate_weighted_average_cost(transactions_df):
    """
    Calculate weighted average cost for each asset from transaction history

    Args:
        transactions_df: DataFrame with columns ['日期', '操作类型', '标的', '数量', '价格(USD)', '金额(USD)']

    Returns:
        dict: {symbol: {'quantity': int, 'avg_cost': float, 'total_cost': float}}
    """
    holdings = defaultdict(lambda: {'buys': [], 'sells': []})

    for _, row in transactions_df.iterrows():
        symbol = row['标的']
        operation = row['操作类型']
        quantity = row['数量']
        price = row['价格(USD)']

        if operation == '买入':
            holdings[symbol]['buys'].append({'qty': quantity, 'price': price})
        elif operation == '卖出':
            holdings[symbol]['sells'].append({'qty': quantity, 'price': price})

    # Calculate net holdings
    result = {}

    for symbol, data in holdings.items():
        # Total bought
        total_bought_qty = sum(b['qty'] for b in data['buys'])
        total_bought_cost = sum(b['qty'] * b['price'] for b in data['buys'])

        # Total sold
        total_sold_qty = sum(s['qty'] for s in data['sells'])

        # Net position
        net_qty = total_bought_qty - total_sold_qty

        if net_qty > 0:
            # Calculate weighted average cost
            # For simplicity, using FIFO assumption for cost basis after sells
            avg_cost = total_bought_cost / total_bought_qty
            total_cost = net_qty * avg_cost

            result[symbol] = {
                'quantity': net_qty,
                'avg_cost': round(avg_cost, 4),
                'total_cost': round(total_cost, 2)
            }

    return result

def format_holdings_csv(holdings_dict):
    """
    Format holdings dictionary into CSV format

    Returns:
        str: CSV formatted string
    """
    lines = ['标的,当前持股数,买入加权平均成本(USD),持仓成本合计(USD),']

    # Sort by symbol
    for symbol in sorted(holdings_dict.keys()):
        data = holdings_dict[symbol]
        line = f"{symbol},{data['quantity']},{data['avg_cost']},{data['total_cost']},"
        lines.append(line)

    return '\n'.join(lines)

def validate_position_limits(holdings_dict, risk_layer_total):
    """
    Validate holdings against position limits

    Position limits (% of risk layer):
    - MSFT: ≤35%
    - QQQ: ≤30%
    - TSLA: ≤15%
    - GLD: ≤15%

    Returns:
        dict: {symbol: {'current_pct': float, 'limit_pct': float, 'within_limit': bool}}
    """
    limits = {
        'MSFT': 35,
        'QQQ': 30,
        'TSLA': 15,
        'GLD': 15
    }

    validation = {}

    for symbol, limit_pct in limits.items():
        if symbol in holdings_dict:
            current_cost = holdings_dict[symbol]['total_cost']
            current_pct = (current_cost / risk_layer_total) * 100
            within_limit = current_pct <= limit_pct

            validation[symbol] = {
                'current_pct': round(current_pct, 2),
                'limit_pct': limit_pct,
                'within_limit': within_limit,
                'status': '✅' if within_limit else '⚠️'
            }

    return validation

def calculate_risk_layer_allocation(holdings_dict, total_capital):
    """
    Calculate risk layer vs safe layer allocation

    Target: Risk Layer 60-70%, Safe Layer 30-40%

    Returns:
        dict with allocation metrics
    """
    total_invested = sum(h['total_cost'] for h in holdings_dict.values())
    risk_layer_pct = (total_invested / total_capital) * 100
    safe_layer_pct = 100 - risk_layer_pct

    within_target = 60 <= risk_layer_pct <= 70

    return {
        'total_invested': round(total_invested, 2),
        'total_capital': total_capital,
        'risk_layer_pct': round(risk_layer_pct, 2),
        'safe_layer_pct': round(safe_layer_pct, 2),
        'within_target': within_target,
        'status': '✅' if within_target else '⚠️'
    }

if __name__ == '__main__':
    # Example usage
    if len(sys.argv) >= 2:
        transactions_file = sys.argv[1]

        # Read transactions
        df = pd.read_csv(transactions_file)

        # Calculate holdings
        holdings = calculate_weighted_average_cost(df)

        print("\n=== Current Holdings ===")
        for symbol, data in sorted(holdings.items()):
            print(f"{symbol}: {data['quantity']} shares @ ${data['avg_cost']:.4f} avg = ${data['total_cost']:.2f}")

        # Format CSV
        csv_output = format_holdings_csv(holdings)
        print("\n=== CSV Output ===")
        print(csv_output)

        # Validate position limits (example with 30000 risk layer)
        if len(sys.argv) >= 3:
            risk_layer_total = float(sys.argv[2])
            validation = validate_position_limits(holdings, risk_layer_total)

            print("\n=== Position Limits Validation ===")
            for symbol, val in validation.items():
                print(f"{symbol}: {val['current_pct']:.2f}% / {val['limit_pct']}% {val['status']}")

    else:
        print("Usage: python update_holdings.py TRANSACTIONS_CSV [RISK_LAYER_TOTAL]")
        print("Example: python update_holdings.py ../../../05_transactions_all.csv 30000")
