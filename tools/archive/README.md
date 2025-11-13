# Archived Tools

This directory contains deprecated scripts that have been replaced by enhanced versions.

## update_prices_yahoo.py (Archived: 2025-11-13)

**Why archived:**
This script was merged into the unified `update_prices.py` located in `.claude/skills/daily-investment-analysis/scripts/`.

**Previous functionality:**
- Fetched daily OHLCV data from Yahoo Finance using urllib
- Could fill blank rows in existing CSV files
- Had hardcoded symbols and target dates

**Replacement:**
The new unified script provides:
- Both append and fill-blanks modes via command-line flags
- Auto-discovery of tickers (no hardcoding needed)
- Cleaner API using yfinance library
- Better error handling and user feedback
- Consistent with other skill scripts

**Usage in new script:**
```bash
# Append new dates (replaces default behavior)
python3 scripts/update_prices.py

# Fill blank rows (replaces this archived script)
python3 scripts/update_prices.py --fill-blanks --target-dates 2025-11-07 2025-11-08
```

**Kept for reference:**
This file is preserved in case we need to reference the urllib-based implementation or the specific date-filling logic in the future.
