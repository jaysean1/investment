# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **investment tracking and order management system** for a 4-asset portfolio (MSFT, QQQ, TSLA, GLD) operated from Sydney timezone. The system follows a **pre-market order workflow** with layered position management, data validation, and transaction tracking.

### Core Philosophy
- All decisions made **pre-market** (Sydney time, US pre-market hours)
- No intraday monitoring or reactive trading
- Layered limit orders based on price intervals
- Data validation against Yahoo Finance (±0.5% tolerance)

## File Structure & Workflow

The repository uses a **6-file sequential pipeline** (numbered 01-06):

| File | Type | Purpose |
|:--|:--|:--|
| `01_investment_objectives.md` | Strategy | Long-term goals, asset allocation framework, position limits |
| `02_collaboration_process.md` | Workflow | Execution protocol and data flow diagram |
| `03_prices_all/` | Data (CSV) | 4 separate CSV files for MSFT/QQQ/TSLA/GLD daily prices |
| `04_order_log.md` | Log | Pre-market order suggestions (reverse chronological) |
| `05_transactions_all.csv` | Data (CSV) | All executed transactions with amounts and rationale |
| `06_holdings_all.csv` | Data (CSV) | Current position summary with cost basis |

### CSV Data Structure

**Price Files** (`03_prices_all/*.csv`):
```
Date, PreMarket_Price, Open, High, Low, Close, Volume, Screenshot_Source, Verified_Yahoo, Notes
```
- `PreMarket_Price`: Recorded during Sydney 21:00-23:00 (US pre-market hours), used for order decision-making
- `Open/High/Low/Close`: Recorded after US market close, complete OHLC data for analysis

**Transactions** (`05_transactions_all.csv`):
```
日期, 操作类型, 标的, 数量, 价格(USD), 金额(USD), 理由/触发条件, 风险盘余额(USD), 累计转回安全盘(USD)
```

**Holdings** (`06_holdings_all.csv`):
```
标的, 当前持股数, 买入加权平均成本(USD), 持仓成本合计(USD)
```

## Data Flow Pipeline

**Two-Phase Daily Workflow:**

**Phase 1 - Pre-Market (Sydney 21:00-23:00):**
```
[Pre-market Price Check]
    → [Record PreMarket_Price in CSV]
    → [04_order_log.md generation]
```

**Phase 2 - Post-Close (After US Market Close):**
```
[OHLC Data Collection]
    → [Yahoo Finance Validation (±0.5%)]
    → [Update Open/High/Low/Close in CSV]
    → [If executed: 05_transactions_all.csv]
    → [06_holdings_all.csv update]
```

## Asset Allocation Framework

### Two-Layer Structure
- **Risk Layer** (60-70%): Active trading in MSFT/QQQ/TSLA
- **Safe Layer** (30-40%): Cash reserves and money market funds

### Position Limits (Risk Layer % only)
| Asset | Type | Max Position | Strategy |
|:--|:--|:--|:--|
| MSFT | Core holding | ≤35% | Long-term growth, buy on pullbacks |
| QQQ | Rhythm position | ≤30% | Dollar-cost averaging + interval buying |
| TSLA | Tactical position | ≤15% | Buy only on technical corrections |
| GLD | Defensive position | ≤15% | Static holding, no chasing |

## Pre-Market Execution Protocol

### Daily Workflow (Sydney Time)

**Phase 1 - Pre-Market Order Setup (21:00-23:00)**
1. **Check Pre-Market Prices**: View real-time pre-market prices (US 4:00-9:30 AM ET)
2. **Record PreMarket_Price**: Update `PreMarket_Price` column in `03_prices_all/*.csv`
3. **Generate Orders**: Create layered limit orders in `04_order_log.md` based on pre-market prices

**Phase 2 - Post-Close Data Recording (After US Market Close)**
4. **Collect OHLC Data**: Gather complete Open/High/Low/Close data
5. **Validation**: Cross-check with Yahoo Finance (tolerance: ±0.5%)
6. **Update Full Prices**: Complete remaining columns in `03_prices_all/*.csv`
7. **Record Transactions**: If orders executed, update `05_transactions_all.csv`
8. **Update Holdings**: Refresh `06_holdings_all.csv` with new cost basis

### Order Structure Pattern
Orders are structured as **layered limit orders** with 3-tier pricing:
```
MSFT: 1 @ $495 / 1 @ $490 / 1 @ $485
```
- Lower prices = wider intervals during downtrends
- Tighter intervals during consolidation
- No orders during strong uptrends (observation mode)

## Key Operational Rules

1. **File Naming**: Use exact names without suffixes like `_updated` or `_final`
2. **Data Validation**: Always mark Yahoo Finance verification status in price files
3. **Transaction Recording**: Include rationale/trigger condition for every trade
4. **Holdings Update**: Recalculate weighted average cost basis after each transaction
5. **Timezone Awareness**: All timestamps in Sydney timezone; execution during US pre-market

## Working with This Codebase

### Adding New Price Data

**Pre-Market Phase (Sydney 21:00-23:00):**
1. Read existing CSV structure from `03_prices_all/[SYMBOL]_prices-Table 1.csv`
2. Add new row with Date and PreMarket_Price (leave OHLC columns empty)
3. Use PreMarket_Price to generate order suggestions

**Post-Close Phase (After US Market Close):**
4. Complete the row with Open, High, Low, Close, Volume data
5. Set `Verified_Yahoo` to "pending" initially
6. Update to "✅" after Yahoo Finance verification (±0.5%)

### Recording Transactions
1. Always include: 日期, 操作类型, 标的, 数量, 价格, 理由
2. Calculate 金额 = 数量 × 价格
3. Update 风险盘余额 based on previous balance ± transaction amount
4. Trigger holdings recalculation immediately after

### Updating Holdings
1. Read all transactions from `05_transactions_all.csv`
2. Calculate weighted average cost: `Σ(quantity × price) / Σ(quantity)`
3. Update 当前持股数 and 持仓成本合计
4. Verify: 持仓成本合计 should equal 当前持股数 × 买入加权平均成本

### Generating Order Suggestions
1. Review recent price action from `03_prices_all/*.csv`
2. Check current holdings from `06_holdings_all.csv`
3. Verify position limits from `01_investment_objectives.md`
4. Generate 3-tier layered orders below current price
5. Add to `04_order_log.md` in reverse chronological order
