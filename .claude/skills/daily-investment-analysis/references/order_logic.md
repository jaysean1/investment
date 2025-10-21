# Order Generation Logic & Decision Tree

This reference defines the systematic approach for generating 3-tier layered limit orders based on market conditions, asset type, and position status.

## Core Order Philosophy

**All orders are limit orders placed pre-market (Sydney time)**
- No intraday monitoring or reactive trading
- Orders represent "willingness to buy at price X" not predictions
- Market decides which orders fill based on price action
- Unfilled orders = "too conservative" which is acceptable

## 3-Tier Order Structure

Every order suggestion follows this format:
```
Symbol(操作): Qty @ Price / Qty @ Price / Qty @ Price
```

Example:
```
MSFT(买入): 1 @ 505 / 1 @ 500 / 1 @ 495
```

### Why 3 Tiers?
1. **Tier 1** (closest to current): Captures minor pullbacks
2. **Tier 2** (medium distance): Targets moderate corrections
3. **Tier 3** (furthest): Catches deeper dips

## Order Interval Decision Tree

### Step 1: Determine Market Phase

```
Calculate 5-day SMA from recent closing prices

IF current_price < SMA_5 × 0.97:
    market_phase = DOWNTREND
ELIF current_price > SMA_5 × 1.03:
    market_phase = UPTREND
ELSE:
    market_phase = CONSOLIDATION
```

### Step 2: Check Position Limit Status

```
Calculate current_position_pct = (Asset Total Cost / Risk Layer Total) × 100

IF current_position_pct >= max_limit:
    STOP - No new orders (observation mode)
ELIF current_position_pct >= max_limit × 0.95:
    REDUCE order quantities to 50%
ELIF current_position_pct >= max_limit × 0.90:
    REDUCE order quantities to 75%
ELSE:
    CONTINUE with normal quantities
```

### Step 3: Apply Phase-Based Intervals

#### DOWNTREND Phase
- **Interval Pattern**: -5%, -10%, -15% below current price
- **Quantity Multiplier**: 1.0× (standard)
- **Rationale**: Wider intervals capture volatility, allow multiple fills
- **Example**: Current $500 → Orders: $475, $450, $425

#### CONSOLIDATION Phase
- **Interval Pattern**: -2%, -4%, -6% below current price
- **Quantity Multiplier**: 1.0× (standard)
- **Rationale**: Tight range requires precise entries
- **Example**: Current $500 → Orders: $490, $480, $470

#### UPTREND Phase
- **Interval Pattern**: NONE (observation mode)
- **Quantity Multiplier**: 0× (no orders)
- **Rationale**: Avoid chasing momentum, wait for pullback
- **Example**: Current $500 → No orders generated

### Step 4: Adjust by Asset Type

Apply quantity multipliers based on asset role:

```
MSFT (Core):     1× - Single shares, steady accumulation
QQQ (Rhythm):    2× - Larger quantities for DCA layer
TSLA (Tactical): 1× - Conservative, only on corrections
GLD (Defensive): 1× - Static holding, minimal activity
```

## Special Order Rules

### MSFT (Core Holding)
- **Never skip**: Always generate orders unless >35% position or strong uptrend
- **Prefer consistency**: Small regular adds over large sporadic buys
- **Long-term focus**: Ignore short-term noise, build steadily

### QQQ (Rhythm Position)
- **Higher quantities**: Use 2-3× multiplier to build DCA layer
- **Flexible intervals**: Can widen in downtrends (e.g., -3%, -6%, -9%)
- **Active management**: Most frequent rebalancing

### TSLA (Tactical Position)
- **Strict conditions**: Only generate orders in DOWNTREND or after >5% correction
- **Conservative sizing**: Always 1× quantity, never aggressive
- **Technical focus**: Respect resistance levels, avoid knife-catching

### GLD (Defensive Position)
- **Minimal activity**: Only add if position <10% of Risk Layer
- **Wide intervals**: -5%, -10%, -15% even in consolidation
- **Never chase**: Accept missing fills, wait patiently

## Order Formatting Guidelines

### Standard Format
```
| Date | Symbol(Operation) | Order String |
```

### Order String Construction
```
f"{qty1} @ ${price1} / {qty2} @ ${price2} / {qty3} @ ${price3}"
```

### Price Rounding
- Round all prices to nearest $1 for readability
- Avoids "$495.47" → use "$495"
- Simplifies order entry and tracking

### Operation Types
- **买入** (Buy): 99% of orders
- **卖出** (Sell): Rare, only for strategic profit-taking

## Order Validation Checklist

Before adding orders to `04_order_log.md`:

- [ ] All prices are BELOW current market price
- [ ] Price intervals follow phase-based logic
- [ ] Quantities respect position limits
- [ ] Format matches existing log structure
- [ ] Date is in Sydney timezone (YYYY-MM-DD)
- [ ] No orders during uptrend phase (unless special condition)

## Edge Cases & Overrides

### When to SKIP Order Generation
1. Position at or above limit (e.g., MSFT ≥35%)
2. Strong uptrend (price >3% above 5-day SMA)
3. Recent large purchase (wait 1-2 days for settlement)
4. Major news event pending (earnings, Fed decision)

### When to MODIFY Standard Intervals
1. **Extreme volatility** (>10% daily range): Widen intervals by 50%
2. **Gap down opening** (>3% below previous close): Add emergency tier at -20%
3. **Near support level**: Cluster orders around technical support

### Manual Overrides
User can always manually adjust:
- Quantities (reduce if uncertain)
- Intervals (widen for patience)
- Skip assets (focus on preferred positions)

The system provides suggestions, not mandates.
