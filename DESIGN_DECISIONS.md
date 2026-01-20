# Design Decisions

## Why Build This?

I needed a pricing foundation for natural gas trading strategies. The fair value calculator helps identify when futures are mispriced relative to spot prices using the cost-of-carry model. It also demonstrates why commodity arbitrage is difficult in practice despite theoretical opportunities.

Key goals:
- Understand convenience yield and its role in commodity pricing
- Implement no-arbitrage bounds with transaction costs
- Support multiple asset classes to show breadth of knowledge
- Create a tool that can be extended to real trading systems

## Object-Oriented Architecture

Used OOP with abstract base classes for extensibility:

```
FairValueCalculator (Abstract Base Class)
    ├── CommodityCalculator
    ├── EquityIndexCalculator
    ├── CurrencyCalculator
    ├── IndividualStockCalculator
    └── CryptocurrencyCalculator
```

Why OOP instead of procedural code?

1. Easy to add new asset types - just inherit from base class
2. Changes to one asset type don't affect others
3. Each component can be tested independently
4. Industry standard for production code

Alternative considered: Procedural with if-else branches for different asset types. Rejected because it becomes messy as you add more assets and violates DRY principle.

## Multiple Asset Classes

Supports commodities, equities, currencies, stocks, and crypto. Each has unique pricing considerations:

**Commodities**: r + u - y (financing + storage - convenience yield)
- Most complex due to convenience yield
- Focus of natural gas thesis

**Equity Indices**: r - q (financing - dividend yield)
- Most feasible for actual arbitrage via ETFs
- High liquidity, low transaction costs

**Currencies**: r_d - r_f (covered interest parity)
- Elegant theoretical relationship
- Very tight spreads

Including multiple asset classes demonstrates understanding of different pricing frameworks and shows the tool has broader applicability beyond one market.

## Convenience Yield Estimation

Cannot observe convenience yield directly - must be implied from market prices.

Formula: `y = r + u - (1/T) × ln(F/S)`

Interpretation:
- High convenience yield → Backwardation → Tight supply
- Low convenience yield → Contango → Ample supply

This is critical for understanding commodity pricing. What looks like mispricing often reflects rational scarcity premium during supply shortages. High convenience yield means the market values having physical inventory now, which can't be arbitraged away.

Example: During winter cold snap, natural gas futures might trade below spot. This looks like arbitrage (buy cheap futures, sell expensive spot) but the high implied convenience yield reflects the value of having gas available immediately. You can't short physical gas, so no arbitrage exists.

## Transaction Cost Modeling

Included transaction costs to calculate no-arbitrage bounds:

```
F_upper_bound = F_fair + Transaction_Costs
F_lower_bound = F_fair - Transaction_Costs
```

Arbitrage only exists if actual price falls outside these bounds. Most "arbitrage opportunities" in academic papers disappear once you account for realistic costs.

Transaction costs vary by asset:
- Commodities: 0.2% spot, 0.1% futures (lower liquidity)
- Equity indices: 0.05% spot, 0.02% futures (very liquid)
- Currencies: 0.01% spot, 0.005% futures (most liquid)

This prevents false signals from noise and mimics how professional traders think about arbitrage.

## Dataclasses and Type Hints

Used dataclasses for parameters and results:

```python
@dataclass
class AssetParameters:
    spot_price: float
    futures_price: float
    time_to_expiry: float
    # ...

    def __post_init__(self):
        if self.spot_price <= 0:
            raise ValueError("Spot price must be positive")
```

Benefits:
- Type safety and IDE autocomplete
- Input validation catches errors early
- Self-documenting code
- Easy serialization

Alternative considered: Plain dictionaries. Rejected because no type checking and easy to typo keys.

## Enums for Constants

Used enums for asset types, market structure, and signals:

```python
class AssetType(Enum):
    COMMODITY = "commodity"
    EQUITY_INDEX = "equity_index"
    CURRENCY = "currency"
```

Prevents typos, enables autocomplete, provides type safety. If I need to refactor, I change the enum in one place rather than finding and replacing strings throughout the code.

## Continuous Compounding

Used continuous compounding (e^rT) instead of discrete:

```python
F = S * np.exp((r + u - y) * T)
```

Reasons:
1. Industry standard for derivatives pricing (Black-Scholes uses this)
2. Standard in Hull's textbook and academic literature
3. Makes solving for convenience yield cleaner: `y = r + u - (1/T) × ln(F/S)`
4. Better for small time intervals and intraday calculations

For very long maturities or matching specific contract conventions, discrete compounding might be more appropriate. But for futures pricing, continuous is standard.

## Testing Approach

Used example-based testing rather than formal unit tests:
- Natural Gas scenarios (contango and backwardation)
- S&P 500 futures fair value
- EUR/USD forward pricing
- Sensitivity analysis

Validated that:
- Fair values are close to actual market prices
- Signals are economically sensible
- Implied convenience yields match inventory patterns
- Edge cases (negative prices, zero time) are handled

Future enhancement would be adding formal pytest unit tests and property-based testing.

## Streamlit Dashboard

Built interactive dashboard instead of command-line tool because:
1. Visualization makes concepts more intuitive
2. Users can adjust parameters and see results update in real-time
3. Professional appearance for presentations
4. Demonstrates full-stack capability

Streamlit chosen because it's pure Python (no HTML/CSS/JS needed) and fast to develop.

Alternative considered: Jupyter notebook. Rejected because less polished for presentations and not a standalone app.

## Why Commodity Arbitrage is Difficult

This is key to understanding why the tool generates signals but they can't be traded:

**Financial assets (equities, currencies):**
- Easy to short
- No storage costs
- Observable inputs
- High liquidity
→ Arbitrage is feasible

**Physical commodities:**
- Cannot short physical inventory
- High storage costs
- Unobservable convenience yield
- Delivery logistics
→ Arbitrage is nearly impossible

What appears as mispricing often reflects high convenience yield, storage constraints, or location/quality differences. Understanding this distinction is critical for interviews.

## Code Documentation

Kept documentation focused on why decisions were made, not just what the code does. Added inline comments for complex calculations and linked to academic papers where applicable. Documented assumptions and limitations.

Avoided excessive docstrings that just repeat what the method name says. Comments explain the reasoning and edge cases.

## Future Extensions

Phase 2: Real-time data integration
- EIA API for nat gas spot prices
- CME DataMine for futures quotes
- Automated daily updates

Phase 3: Machine learning
- Predict convenience yield from inventory and weather data
- Regime classification
- Seasonal pattern recognition

Phase 4: Trading integration
- Broker API connections
- Automated execution
- Risk management

Haven't implemented these yet because Phase 1 demonstrates core understanding and is appropriate for educational/interview purposes. Real trading requires extensive testing and risk management.

## Interview Talking Points

30-second pitch:
"I built a multi-asset fair basis indicator using object-oriented Python. The key design choice was using abstract base classes with asset-specific calculators for extensibility. I focused on transaction cost modeling because most academic arbitrage opportunities disappear once you account for realistic costs. The tool demonstrates why commodity arbitrage is difficult despite theoretical opportunities."

Key points to emphasize:
1. OOP for extensibility
2. Transaction costs for realistic assessment
3. Convenience yield for commodity understanding
4. Multi-asset support for breadth
5. Understands theory AND practical limitations
