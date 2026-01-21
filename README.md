# Fair Basis Arbitrage Indicator

Multi-asset futures fair value calculator and arbitrage signal generator based on cost-of-carry model.

## Overview

This project implements a derivatives pricing system that calculates the theoretical fair value of futures contracts across multiple asset classes. The core uses the cost-of-carry model to determine what futures prices should be given spot prices, interest rates, and carrying costs.

The tool then compares actual market futures prices to theoretical fair value to identify potential arbitrage opportunities. However, the implementation also demonstrates why commodity arbitrage is practically difficult despite theoretical opportunities.

## Supported Asset Classes

**Commodities** (natural gas, oil, gold)
- Formula: F = S × e^((r + u - y)T)
- Includes convenience yield estimation
- Storage costs modeled

**Equity Indices** (S&P 500, NASDAQ)
- Formula: F = S × e^((r - q)T)
- Dividend yield handling
- Feasible arbitrage via ETFs

**Currencies** (EUR/USD, major pairs)
- Formula: F = S × e^((r_d - r_f)T)
- Covered interest parity
- Highly liquid, tight spreads

**Individual Stocks**
- Discrete dividend handling
- Repo rate considerations

**Cryptocurrencies**
- Staking yield incorporated
- Framework ready for extension

## Cost-of-Carry Model

The fundamental relationship:

```
F* = S × e^(cost_of_carry × T)
```

Where cost of carry depends on asset type:

| Asset | Cost of Carry | Components |
|-------|---------------|------------|
| Commodity | r + u - y | financing + storage - convenience yield |
| Equity Index | r - q | financing - dividend yield |
| Currency | r_d - r_f | domestic rate - foreign rate |
| No Income | r | financing only |

Variables:
- S = Current spot price
- F* = Fair (theoretical) futures price
- r = Risk-free rate (SOFR)
- u = Storage cost rate
- y = Convenience yield
- q = Dividend yield
- T = Time to expiration (years)

## Convenience Yield

Cannot be observed directly - must be implied from market prices.

Given: F = S × e^((r + u - y)T)

Solve for y:
```
y = r + u - (1/T) × ln(F/S)
```

Interpretation:
- High convenience yield → Backwardation (F < S) → Tight supply
- Low convenience yield → Contango (F > S) → Ample supply

This is key to understanding commodity pricing and why apparent mispricings often reflect rational scarcity pricing rather than arbitrage opportunities.

## Arbitrage Signal Logic

Calculate no-arbitrage bounds:
```
F_upper = F* + Transaction_Costs
F_lower = F* - Transaction_Costs
```

Signal generation:
```
If F_actual > F_upper:
    → Cash-and-carry arbitrage (buy spot, sell futures)

If F_actual < F_lower:
    → Reverse cash-and-carry (sell spot, buy futures)

Otherwise:
    → No arbitrage (within bounds)
```

Transaction costs by asset:
- Commodities: 0.2% spot, 0.1% futures
- Equity indices: 0.05% spot, 0.02% futures
- Currencies: 0.01% spot, 0.005% futures

## Why Commodity Arbitrage is Difficult

**Financial assets (equities, currencies):**
- Easy to short
- No storage costs
- Observable inputs
- High liquidity
- Cash settlement
→ Arbitrage is feasible

**Physical commodities:**
- Cannot short physical inventory
- High storage costs
- Unobservable convenience yield
- Delivery logistics (location, quality, timing)
- Physical settlement required
→ Arbitrage is nearly impossible

What appears as "mispricing" in commodities often reflects high convenience yield during supply shortages, storage constraints, or location/quality differences.

## Usage

Run sample demonstration:
```bash
python sample_demonstration.py
```

This shows:
- Natural gas analysis (contango and backwardation scenarios)
- S&P 500 futures fair value
- EUR/USD forward pricing
- Sensitivity analysis

Launch interactive dashboard:
```bash
streamlit run dashboard.py
```

Features:
- Real-time parameter adjustment
- Basis deviation gauges
- No-arbitrage bounds visualization
- Cost-of-carry breakdown
- CSV export

## Validation

Validation approach:
1. Hand calculations verified against manual computations
2. Textbook problems compared to John Hull examples
3. Market data checked against Bloomberg/CME fair values
4. Economic sense validated (monotonicity, limiting cases)
5. Cross-validation via implied convenience yield round-trip testing

Run sensitivity analysis:
```bash
python sample_demonstration.py
```

Tests fair value sensitivity to:
- Convenience yield (0% to 15%)
- Transaction costs (0.1% to 2%)
- Time to expiry (1 day to 1 year)

