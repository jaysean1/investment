---
name: daily-investment-analysis
description: This skill should be used for daily pre-market investment analysis workflows. Use when the user provides screenshot inputs of stock prices (MSFT/QQQ/TSLA/GLD), requests order generation, needs to record transactions, or wants to update portfolio holdings. Operates on Sydney timezone with US pre-market execution logic.
---

# Daily Investment Analysis

## Overview

This skill automates the complete daily pre-market investment workflow for a 4-asset portfolio (MSFT, QQQ, TSLA, GLD). Execute this workflow when receiving daily price screenshots or when the user requests order generation, transaction recording, or holdings updates.

**Core Workflow**: Pre-Market Price Input (Evening) → Market Close Data Update (Next Day) → Yahoo Validation → Order Generation → Transaction Recording → Holdings Refresh

## When to Use This Skill

Trigger this skill when:
- User provides **pre-market prices** in the evening (for next trading day order planning)
- User provides screenshot inputs for daily prices (any of MSFT/QQQ/TSLA/GLD)
- User requests pre-market order suggestions
- User reports executed transactions that need recording
- User wants portfolio holdings recalculated
- User asks for position limit validation

**Timezone Context**: All operations occur in Sydney timezone during US pre-market hours. User provides pre-market prices in the evening for next-day order planning.

## Workflow Decision Tree

```
START
  ↓
Has user provided pre-market prices (evening)?
  ├─ YES → Proceed to Phase 0: Pre-Market Price Recording
  └─ NO → Skip to Phase 1
          ↓
Phase 0: Pre-Market Price Recording (EVENING - Sydney time)
  ├─ User provides pre-market prices for next trading day
  ├─ Record in Pre_Market_Price column with empty OHLC
  └─ Generate preliminary order suggestions
          ↓
Phase 1: Market Close Data Update (NEXT DAY)
  ├─ Fetch actual market data using update_prices.py
  ├─ Update OHLC columns for rows with Pre_Market_Price
  ├─ Validate against Yahoo Finance (±0.5% tolerance)
  └─ Keep Pre_Market_Price for comparison
          ↓
Phase 2: Order Generation
  ├─ Analyze recent price trends (detect market phase)
  ├─ Check current position limits
  ├─ Generate 3-tier layered orders
  └─ Append to 04_order_log.md
          ↓
Has user reported executed transactions?
  ├─ YES → Proceed to Phase 3: Transaction Recording
  └─ NO → END (orders generated, workflow complete)
          ↓
Phase 3: Transaction Recording
  ├─ Record in 05_transactions_all.csv
  └─ Trigger Phase 4: Holdings Update
          ↓
Phase 4: Holdings Update
  ├─ Calculate weighted average cost
  ├─ Update 06_holdings_all.csv
  └─ Validate position limits
          ↓
END (full workflow complete)
```

## Phase 0: Pre-Market Price Recording (NEW)

### Overview
User provides pre-market prices every evening (Sydney time) for the next trading day. This enables early order planning before the actual market data is available.

### Step 0.1: Receive Pre-Market Prices

User provides pre-market prices in the format:
```
Pre-market prices for 2025-11-07:
MSFT $500
QQQ $620
TSLA $450
GLD $365
```

### Step 0.2: Add Pre-Market Price Rows

**Important**: At this stage, we only record the pre-market price. OHLC data remains empty until actual market close.

Run Python script to add pre-market placeholder:
```python
python3 << 'EOF'
import pandas as pd
from pathlib import Path

DATA_DIR = Path('/Users/qiansui/Downloads/xinyihan/investment/structure/03_prices_all')

premarket_data = {
    'MSFT': 500.0,
    'QQQ': 620.0,
    'TSLA': 450.0,
    'GLD': 365.0
}

date = '2025-11-07'

for ticker, premarket_price in premarket_data.items():
    csv_path = DATA_DIR / f'{ticker}_prices-Table 1.csv'
    df = pd.read_csv(csv_path)

    # Check if date already exists
    if date in df['Date'].values:
        print(f"⚠️  {ticker}: Date {date} already exists, skipping")
        continue

    # Add placeholder row with only pre-market price
    new_row = {
        'Date': date,
        'Open': '',
        'High': '',
        'Low': '',
        'Close': '',
        'Volume': '',
        'Pre_Market_Price': premarket_price,
        'Screenshot_Source': 'user_premarket',
        'Verified_Yahoo': 'pending',
        'Notes': 'pre-market input, awaiting market close data'
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(csv_path, index=False)
    print(f"✅ {ticker}: Added pre-market price ${premarket_price}")

EOF
```

### Step 0.3: Generate Preliminary Orders

Based on pre-market prices, generate order suggestions for next trading day. This allows user to prepare orders in advance.

**Next Step**: Wait for actual market close, then proceed to Phase 1 to fetch real OHLC data.

## Phase 1: Market Close Data Update

### Overview
After market closes, fetch actual OHLC data and update the rows that have pre-market prices.

### Step 1.1: Run Update Script

Use the `update_prices.py` script to automatically fetch Yahoo Finance data:

```bash
python3 update_prices.py
```

This script will:
- Find dates with empty OHLC but with Pre_Market_Price
- Fetch actual market data from Yahoo Finance
- Fill in Open, High, Low, Close, Volume
- Keep the Pre_Market_Price for comparison
- Mark as verified with ✅

### Step 1.2: Validate Pre-Market vs Actual

After update, compare pre-market predictions with actual close:

```python
# Check last row with pre-market price
import pandas as pd
df = pd.read_csv('03_prices_all/MSFT_prices-Table 1.csv')
last_row = df.iloc[-1]

if last_row['Pre_Market_Price']:
    premarket = float(last_row['Pre_Market_Price'])
    actual = float(last_row['Close'])
    diff = actual - premarket
    diff_pct = (diff / premarket) * 100
    print(f"Pre-market: ${premarket:.2f}, Actual: ${actual:.2f}, Diff: {diff_pct:+.2f}%")
```

### Step 1.3: Extract Price Data (Historical Method - For Screenshots)

User provides 4 screenshots containing daily prices for:
- MSFT (Microsoft)
- QQQ (Invesco QQQ Trust)
- TSLA (Tesla)
- GLD (SPDR Gold Trust)

Extract the following data points from each screenshot:
- Date (YYYY-MM-DD format)
- Open price
- High price
- Low price
- Close price
- Volume (if available)

**Note**: This method is now optional since `update_prices.py` automatically fetches data from Yahoo Finance.

### Step 1.4: Updated CSV Format (With Pre_Market_Price Column)

**NEW CSV Structure**:
```csv
Date,Open,High,Low,Close,Volume,Pre_Market_Price,Screenshot_Source,Verified_Yahoo,Notes
2025-11-06,505.36,505.7,495.81,497.1,27048995,,yahoo_api,✅,
2025-11-07,,,,,500.0,user_premarket,pending,pre-market input
```

**Column Definitions**:
- `Date`: Trading date (YYYY-MM-DD)
- `Open`, `High`, `Low`, `Close`, `Volume`: Market data (from Yahoo Finance)
- **`Pre_Market_Price`**: Evening pre-market price provided by user (NEW)
- `Screenshot_Source`: Data source (yahoo_api, user_premarket, user_screenshot)
- `Verified_Yahoo`: Validation status (✅, pending, ⚠️, ❌)
- `Notes`: Additional information

### Data Flow Examples

**Example 1: Pre-Market to Market Close Flow**
```
Evening (Sydney time):
Date,Open,High,Low,Close,Volume,Pre_Market_Price,Screenshot_Source,Verified_Yahoo,Notes
2025-11-07,,,,,500.0,user_premarket,pending,pre-market input

Next Day After Market Close:
Date,Open,High,Low,Close,Volume,Pre_Market_Price,Screenshot_Source,Verified_Yahoo,Notes
2025-11-07,505.36,505.7,495.81,497.1,27048995,500.0,yahoo_api,✅,
```

**Example 2: Direct Yahoo Finance Update (No Pre-Market)**
```
Date,Open,High,Low,Close,Volume,Pre_Market_Price,Screenshot_Source,Verified_Yahoo,Notes
2025-11-08,500.5,502.3,498.1,501.2,25000000,,yahoo_api,✅,
```

### Update Price CSV Files

Update the corresponding CSV file in `03_prices_all/`:
- `MSFT_prices-Table 1.csv`
- `QQQ_prices-Table 1.csv`
- `TSLA_prices-Table 1.csv`
- `GLD_prices-Table 1.csv`

**Rules**:
- Append new rows (do not modify existing data)
- If pre-market price provided: Set `Pre_Market_Price`, leave OHLC empty, mark as "pending"
- If market data available: Fill OHLC, set `Screenshot_Source` to "yahoo_api", mark as ✅
- Leave `Notes` empty unless there's an issue

## Phase 2: Order Generation

### Step 2.1: Detect Market Phase

Read the last 10 closing prices from the updated CSV files to determine market phase for each asset:

**Phase Detection Logic** (see `references/order_logic.md` for details):
```
5-day SMA = Average of last 5 closing prices

IF current_close < SMA_5 × 0.97:
    Phase = DOWNTREND (wider intervals)
ELIF current_close > SMA_5 × 1.03:
    Phase = UPTREND (observation mode, no orders)
ELSE:
    Phase = CONSOLIDATION (tight intervals)
```

### Step 2.2: Check Position Limits

Read current holdings from `06_holdings_all.csv`:
```csv
标的,当前持股数,买入加权平均成本(USD),持仓成本合计(USD),
MSFT,19,488.3435,9278.53,
QQQ,16,575.0625,9201,
TSLA,3,432.6667,1298,
GLD,2,352,704,
```

Calculate current position percentages (see `references/position_limits.md`):
- MSFT: ≤35% of Risk Layer
- QQQ: ≤30% of Risk Layer
- TSLA: ≤15% of Risk Layer
- GLD: ≤15% of Risk Layer

**If any position ≥ limit**: SKIP order generation for that asset.

### Step 2.3: Generate 3-Tier Orders

Use the order calculation logic (or manually apply):

**DOWNTREND Intervals**: -5%, -10%, -15% below current price
**CONSOLIDATION Intervals**: -2%, -4%, -6% below current price
**UPTREND**: No orders (observation mode)

**Quantity Adjustments**:
- MSFT (Core): 1× standard
- QQQ (Rhythm): 2× for DCA layer
- TSLA (Tactical): 1× conservative
- GLD (Defensive): 1× static

**Example Output**:
```
MSFT at $513.58 (CONSOLIDATION):
  1 @ $503 / 1 @ $493 / 1 @ $483

QQQ at $575.50 (DOWNTREND):
  2 @ $547 / 2 @ $518 / 2 @ $489
```

### Step 2.4: Update Order Log

Append new orders to `04_order_log.md` in reverse chronological order:

```markdown
| Date | Symbol | Suggested Orders (USD) |
|:--|:--|:--|
| 2025-10-20 | MSFT(买入) | 1 @ 505 / 1 @ 500 / 1 @ 495 |
| 2025-10-20 | QQQ(买入) | 2 @ 570 / 2 @ 560 / 2 @ 550 |
| 2025-10-20 | TSLA(买入) | 1 @ 430 / 1 @ 425 / 1 @ 420 |
| 2025-10-20 | GLD(买入) | 1 @ 350 / 1 @ 345 / 1 @ 340 |
```

**Format Rules**:
- Date in YYYY-MM-DD format (Sydney timezone)
- Symbol with operation in Chinese: `Symbol(买入)` or `Symbol(卖出)`
- Prices rounded to nearest $1
- Insert new rows at the TOP of the table (after header)

## Phase 3: Transaction Recording

**Trigger**: User reports that orders were executed.

### Step 3.1: Collect Transaction Details

Ask the user for:
- Date of execution
- Symbol (MSFT/QQQ/TSLA/GLD)
- Quantity
- Execution price
- Reason/trigger condition (e.g., "区间回补", "震荡低吸")

### Step 3.2: Update Transactions CSV

Append to `05_transactions_all.csv`:

```csv
日期,操作类型,标的,数量,价格(USD),金额(USD),理由/触发条件,风险盘余额(USD),累计转回安全盘(USD)
2025-10-20,买入,MSFT,1,505,505,区间回补,,
```

**CSV Rules**:
- `日期`: YYYY-MM-DD format
- `操作类型`: "买入" or "卖出"
- `标的`: MSFT/QQQ/TSLA/GLD
- `金额(USD)`: = 数量 × 价格(USD)
- `理由/触发条件`: Brief Chinese explanation
- `风险盘余额` and `累计转回安全盘`: Leave empty (user updates manually)

### Step 3.3: Trigger Holdings Update

After recording transaction, immediately proceed to Phase 4.

## Phase 4: Holdings Update

### Step 4.1: Calculate Weighted Average Cost

Use the holdings update script or manually calculate:

```bash
python scripts/update_holdings.py ../../../05_transactions_all.csv
```

**Calculation Logic**:
1. Read all transactions from `05_transactions_all.csv`
2. For each symbol:
   - Sum all buys: `total_bought_qty`, `total_bought_cost`
   - Sum all sells: `total_sold_qty`
   - Net quantity: `net_qty = total_bought_qty - total_sold_qty`
   - Weighted avg cost: `avg_cost = total_bought_cost / total_bought_qty`
   - Total cost: `total_cost = net_qty × avg_cost`

### Step 4.2: Update Holdings CSV

Write updated holdings to `06_holdings_all.csv`:

```csv
标的,当前持股数,买入加权平均成本(USD),持仓成本合计(USD),
GLD,2,352,704,
MSFT,20,490.1234,9802.47,
QQQ,16,575.0625,9201,
TSLA,3,432.6667,1298,
```

**Format Rules**:
- Sort alphabetically by symbol
- Round `买入加权平均成本` to 4 decimal places
- Round `持仓成本合计` to 2 decimal places
- Include trailing comma on each line

### Step 4.3: Validate Position Limits

Check if any position exceeds limits:

```
MSFT: (9802.47 / Risk_Layer_Total) × 100 = ?% (limit: 35%)
QQQ: (9201 / Risk_Layer_Total) × 100 = ?% (limit: 30%)
TSLA: (1298 / Risk_Layer_Total) × 100 = ?% (limit: 15%)
GLD: (704 / Risk_Layer_Total) × 100 = ?% (limit: 15%)
```

**If Risk Layer Total is unknown**, ask user or estimate from sum of holdings.

**Alert user** if any position exceeds 90% of limit.

## Reference Materials

### Position Limits Framework
See `references/position_limits.md` for detailed information on:
- Two-layer capital structure (Risk Layer / Safe Layer)
- Asset allocation targets (60-70% / 30-40%)
- Position limits per asset
- Rebalancing triggers

### Order Logic & Decision Tree
See `references/order_logic.md` for detailed information on:
- 3-tier order structure rationale
- Phase-based interval calculations
- Asset-specific quantity multipliers
- Edge cases and manual overrides

## Utility Scripts

### 1. validate_yahoo_price.py
**Purpose**: Cross-check price data with Yahoo Finance (±0.5% tolerance)

**Usage**:
```bash
python scripts/validate_yahoo_price.py SYMBOL DATE PRICE [PRICE_TYPE]
```

**Example**:
```bash
python scripts/validate_yahoo_price.py MSFT 2025-10-20 513.58 Close
```

### 2. calculate_order_intervals.py
**Purpose**: Generate 3-tier order levels based on market phase and asset type

**Usage**:
```bash
python scripts/calculate_order_intervals.py SYMBOL CURRENT_PRICE [MARKET_PHASE] [ASSET_TYPE]
```

**Example**:
```bash
python scripts/calculate_order_intervals.py MSFT 513.58 consolidation core
```

### 3. update_holdings.py
**Purpose**: Calculate weighted average cost and validate position limits

**Usage**:
```bash
python scripts/update_holdings.py TRANSACTIONS_CSV [RISK_LAYER_TOTAL]
```

**Example**:
```bash
python scripts/update_holdings.py 05_transactions_all.csv 30000
```

## Important Notes

### File Naming Convention
- **NEVER** use suffixes like `_updated`, `_final`, `_new`
- Always use exact filenames: `03_prices_all/*.csv`, `04_order_log.md`, etc.
- Repository uses 01-06 numbering system consistently

### Timezone Awareness
- All operations occur in **Sydney timezone**
- Corresponds to **US pre-market hours** (evening Sydney time)
- Date format always YYYY-MM-DD

### Data Validation
- Always validate prices against Yahoo Finance before updating CSVs
- Mark validation status in `Verified_Yahoo` column
- Alert user if validation fails (>±0.5% difference)

### Order Philosophy
- Orders are **suggestions**, not predictions
- Market determines which orders fill
- No orders filled = "挂得稳" (patient positioning)
- Never chase uptrends

### Position Management
- Check limits BEFORE generating orders
- Stop orders if position ≥ limit
- Reduce quantities if position ≥ 90% of limit
- Maintain Safe Layer minimum 30% for psychological stability

## Workflow Summary

**Daily Routine** (typical execution):
1. User provides 4 price screenshots (MSFT/QQQ/TSLA/GLD)
2. Validate each price against Yahoo Finance
3. Update all 4 CSV files in `03_prices_all/`
4. Analyze market phase for each asset
5. Generate 3-tier orders respecting position limits
6. Append orders to `04_order_log.md`
7. Present order suggestions to user
8. **If executions reported**: Record in `05_transactions_all.csv` and update `06_holdings_all.csv`

**Estimated Time**: 5-10 minutes for full workflow (validation + order generation)

**Success Criteria**:
- ✅ All prices validated within ±0.5%
- ✅ Orders follow phase-based logic
- ✅ No position limit violations
- ✅ All files updated with correct format
- ✅ User receives clear order suggestions
