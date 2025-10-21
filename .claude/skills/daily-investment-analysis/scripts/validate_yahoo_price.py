#!/usr/bin/env python3
# location: .claude/skills/daily-investment-analysis/scripts/validate_yahoo_price.py
# This script validates price data against Yahoo Finance with ±0.5% tolerance
# Returns validation status for daily price inputs

import yfinance as yf
from datetime import datetime
import sys

def validate_price(symbol, date, price, price_type='Close'):
    """
    Validate a price against Yahoo Finance data

    Args:
        symbol: Stock ticker (e.g., 'MSFT', 'QQQ', 'TSLA', 'GLD')
        date: Date string in format 'YYYY-MM-DD'
        price: Price to validate (float)
        price_type: Type of price ('Open', 'High', 'Low', 'Close')

    Returns:
        dict with keys: 'valid', 'yahoo_price', 'difference_pct', 'status_emoji'
    """
    try:
        # Fetch data from Yahoo Finance
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=date, end=date)

        if data.empty:
            return {
                'valid': False,
                'yahoo_price': None,
                'difference_pct': None,
                'status_emoji': '❌',
                'error': f'No data available for {symbol} on {date}'
            }

        # Get the yahoo price for the specified type
        yahoo_price = float(data[price_type].iloc[0])

        # Calculate percentage difference
        difference_pct = abs((price - yahoo_price) / yahoo_price * 100)

        # Validate within ±0.5% tolerance
        valid = difference_pct <= 0.5

        return {
            'valid': valid,
            'yahoo_price': yahoo_price,
            'difference_pct': difference_pct,
            'status_emoji': '✅' if valid else '⚠️',
            'error': None
        }

    except Exception as e:
        return {
            'valid': False,
            'yahoo_price': None,
            'difference_pct': None,
            'status_emoji': '❌',
            'error': str(e)
        }

def validate_full_day(symbol, date, open_price, high_price, low_price, close_price):
    """
    Validate all four prices for a trading day

    Returns:
        dict with validation results for each price type
    """
    results = {
        'Open': validate_price(symbol, date, open_price, 'Open'),
        'High': validate_price(symbol, date, high_price, 'High'),
        'Low': validate_price(symbol, date, low_price, 'Low'),
        'Close': validate_price(symbol, date, close_price, 'Close')
    }

    # Overall validation status
    all_valid = all(r['valid'] for r in results.values() if r['valid'] is not False)

    return {
        'overall_valid': all_valid,
        'overall_emoji': '✅' if all_valid else '⚠️',
        'details': results
    }

if __name__ == '__main__':
    # Command line usage example
    if len(sys.argv) >= 4:
        symbol = sys.argv[1]
        date = sys.argv[2]
        price = float(sys.argv[3])
        price_type = sys.argv[4] if len(sys.argv) > 4 else 'Close'

        result = validate_price(symbol, date, price, price_type)
        print(f"Symbol: {symbol}")
        print(f"Date: {date}")
        print(f"Input {price_type}: ${price:.2f}")
        print(f"Yahoo {price_type}: ${result['yahoo_price']:.2f}" if result['yahoo_price'] else "N/A")
        print(f"Difference: {result['difference_pct']:.2f}%" if result['difference_pct'] else "N/A")
        print(f"Status: {result['status_emoji']}")
        if result['error']:
            print(f"Error: {result['error']}")
    else:
        print("Usage: python validate_yahoo_price.py SYMBOL DATE PRICE [PRICE_TYPE]")
        print("Example: python validate_yahoo_price.py MSFT 2025-10-20 513.58 Close")
