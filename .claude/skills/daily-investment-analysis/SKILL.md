---
name: daily-investment-analysis
description: This skill should be used for daily pre-market investment analysis workflows. Use when the user provides screenshot inputs of stock prices (MSFT/QQQ/TSLA/GLD), requests order generation, needs to record transactions, or wants to update portfolio holdings. Operates on Sydney timezone with US pre-market execution logic.
---

# Daily Investment Analysis

## Overview

This skill automates the complete daily pre-market investment workflow for a 4-asset portfolio (MSFT, QQQ, TSLA, GLD). Execute this workflow when receiving daily price screenshots or when the user requests order generation, transaction recording, or holdings updates.

**Core Workflow**: Screenshot Input → Yahoo Validation → Price Update → Order Generation → Transaction Recording → Holdings Refresh

## When to Use This Skill

Trigger this skill when:
- User provides screenshot inputs for daily prices (any of MSFT/QQQ/TSLA/GLD)
- User requests pre-market order suggestions
- User reports executed transactions that need recording
- User wants portfolio holdings recalculated
- User asks for position limit validation

**Timezone Context**: All operations occur in Sydney timezone during US pre-market hours.

## Workflow Decision Tree

```
START
  ↓
Has user provided price screenshots?
  ├─ YES → Proceed to Phase 1: Data Input & Validation
  └─ NO → Ask user for screenshot inputs
          ↓
Phase 1: Data Input & Validation
  ├─ Extract price data from screenshots (Open/High/Low/Close)
  ├─ Validate against Yahoo Finance (±0.5% tolerance)
  └─ Update 03_prices_all/*.csv files
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

## Phase 1: Data Input & Validation

### Step 1.1: Extract Price Data

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

### Step 1.2: Validate Against Yahoo Finance

Use the validation script to cross-check prices:

```bash
python scripts/validate_yahoo_price.py MSFT 2025-10-20 513.58 Close
```

**Validation Criteria**:
- Tolerance: ±0.5% difference from Yahoo Finance
- Status: `✅` (valid) or `⚠️` (warning) or `❌` (error)

**Important**: If validation shows `⚠️` or `❌`, inform the user and ask whether to proceed with the data or request correction.

### Step 1.3: Update Price CSV Files

Update the corresponding CSV file in `03_prices_all/`:
- `MSFT_prices-Table 1.csv`
- `QQQ_prices-Table 1.csv`
- `TSLA_prices-Table 1.csv`
- `GLD_prices-Table 1.csv`

**CSV Format**:
```csv
Date,Open,High,Low,Close,Volume,Screenshot_Source,Verified_Yahoo,Notes
2025-10-20,509.04,515.48,507.31,513.58,19798500,user_screenshot,✅,
```

**Rules**:
- Append new rows (do not modify existing data)
- Set `Screenshot_Source` to "user_screenshot"
- Set `Verified_Yahoo` to validation status emoji
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
