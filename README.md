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

## Installation and Usage

Install dependencies:
```bash
pip install -r requirements.txt
```

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

## Code Example

```python
from futures_pricer import FairBasisIndicator, AssetParameters, AssetType

# Initialize
indicator = FairBasisIndicator()

# Natural Gas parameters
params = AssetParameters(
    spot_price=2.50,
    futures_price=2.65,
    time_to_expiry=0.25,
    risk_free_rate=0.05,
    storage_cost_rate=0.06,
    convenience_yield=0.02,
    spot_transaction_cost=0.002,
    futures_transaction_cost=0.001,
    asset_name="Natural Gas",
    asset_type=AssetType.COMMODITY
)

# Calculate and display
result = indicator.calculate(params)
indicator.print_summary(result)
```

## Project Structure

```
fair_basis_arbitrage/
├── futures_pricer.py           # Main pricing engine (383 lines)
│   ├── FairBasisIndicator
│   ├── CommodityCalculator
│   ├── EquityIndexCalculator
│   ├── CurrencyCalculator
│   └── Other calculators
├── sample_demonstration.py     # Working examples
├── dashboard.py                # Streamlit visualization
├── educational_guide.py        # Learning resources
├── DESIGN_DECISIONS.md         # Architecture explanation
├── INTERVIEW_GUIDE.md          # Q&A preparation
└── requirements.txt
```

## Architecture

Object-oriented design with abstract base classes for extensibility. Each asset type has its own calculator class inheriting from `FairValueCalculator` base class.

Adding a new asset type requires:
1. Create new calculator class
2. Implement `calculate_fair_futures()` method
3. Define asset-specific cost of carry
4. Register in asset type enum

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

## Key Insights

**Why this matters:**

This tool provides the pricing foundation for natural gas trading strategies. By tracking implied convenience yield, you can detect changes in market's view of supply tightness.

**Integration with broader strategy:**
```
Fair Basis Tool (this project)
    + Weather Forecasting (NOAA data)
    + Machine Learning (predict convenience yield)
    + Inventory Data (EIA reports)
    = Natural Gas Trading Strategy
```

**What you learn:**

1. Demonstrates cost-of-carry pricing across multiple assets
2. Shows why commodity arbitrage is difficult (practical limitations)
3. Implements convenience yield estimation
4. Models transaction costs realistically
5. Extensible OOP architecture

## Interview Talking Points

**2-minute pitch:**

"I built a multi-asset fair basis arbitrage indicator that calculates theoretical fair value for futures contracts.

The core uses the cost-of-carry model with asset-specific formulas. For commodities like natural gas, I implemented convenience yield estimation - this is the key to understanding why apparent mispricings often aren't arbitrage opportunities.

The tool includes transaction cost modeling to determine no-arbitrage bounds, because most theoretical arbitrage opportunities disappear once you account for realistic trading costs.

I used object-oriented Python with abstract base classes for extensibility - adding a new asset type just requires inheriting from the base calculator class.

The key insight is demonstrating why commodity arbitrage is so much harder than financial asset arbitrage. You can't short physical commodities, storage is expensive, and convenience yield is unobservable. What looks like mispricing often reflects rational scarcity pricing."

**Common questions:**

Q: Can you actually arbitrage commodities?
A: No, not practically. You can't short physical inventory, storage is expensive, and logistics make it nearly impossible. Financial assets like equities are much more feasible.

Q: What's the hardest part?
A: Estimating convenience yield. It's unobservable and depends on inventory levels, seasonal demand, and supply disruptions. This is where machine learning could help.

Q: How would you extend this?
A: Add real-time data feeds (EIA for nat gas, CME for futures), incorporate weather forecasting to predict convenience yield, and build a full term structure analysis.

## Limitations

1. Transaction costs are estimates and may vary significantly in practice
2. Commodity arbitrage is practically infeasible despite theoretical signals
3. Convenience yield estimation requires accurate spot/futures quotes
4. Model assumes continuous compounding and no market frictions beyond transaction costs

## Dependencies

```
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.10.0
streamlit>=1.28.0
plotly>=5.17.0
```

See `requirements.txt` for complete list.

## Documentation

See `INTERVIEW_GUIDE.md` for comprehensive Q&A preparation covering:
- Technical concept explanations
- Common interview questions with answers
- 60-second project pitch
- Scenario-based walkthroughs

See `DESIGN_DECISIONS.md` for architecture explanations:
- Why OOP?
- Why dataclasses?
- Why continuous compounding?
- Every design choice explained

## Disclaimer

This project is for educational and interview purposes only. Not financial advice. Commodity arbitrage is practically difficult despite theoretical feasibility. Do not attempt real trading without physical storage infrastructure, deep market knowledge, significant capital, and professional risk management.

## License

MIT License

---

Last Updated: January 2026
