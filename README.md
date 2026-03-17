# Fair Basis Arbitrage Indicator

**November 2025 -- December 2025** | Zaid Annigeri | Master of Quantitative Finance, Rutgers Business School

> Multi-asset derivatives pricing system that analyzes why equity/currency arbitrage works while commodity arbitrage fails.

## Project Overview

This project implements a cost-of-carry model to calculate theoretical fair values for futures contracts across five asset classes. Analysis of simulated signal data across asset classes shows:

- **Financial assets (equities, currencies)**: 68-71% arbitrage win rate, Sharpe ratios 1.8-2.3
- **Commodities (natural gas, gold)**: Only 3% of signals exploitable, negative Sharpe ratios

### Key Findings

- **3 Illustrative Case Studies**: S&P 500 Jan 2023 (+1.8 bps profit), Natural Gas Mar 2022 (58% conv. yield, FAILED), EUR/USD Oct 2023 (+1.8 bps profit). These use hardcoded market parameters (spot prices, rates) with constructed futures prices to illustrate model behavior -- not live-fetched data.
- **Signal Performance**: 170 S&P 500 signals with 70.6% win rate and +90.7 bps cumulative profit (simulated)

---

## Quick Start

### Prerequisites
```bash
Python 3.8+
numpy, pandas, scipy, matplotlib, seaborn, yfinance
```

### Installation
```bash
# Clone repository
git clone https://github.com/Zaid282802/fair-basis-arbitrage.git
cd fair-basis-arbitrage

# Install dependencies
pip install numpy pandas scipy matplotlib seaborn yfinance requests
```

### Run Analysis
```bash
# Run basic usage demonstration
python sample_demonstration.py

# Run illustrative case studies with hardcoded market parameters
python src/historical_validation.py

# Generate 7 portfolio visualizations (300 DPI)
python src/create_visualizations.py
```

**Output**:
- `sample_demonstration.py`: Shows natural gas, S&P 500, and EUR/USD pricing examples
- `historical_validation.py`: Runs case studies using hardcoded market parameters (2022-2023)
- `create_visualizations.py`: Generates 7 charts saved to `visualizations/`

**Data**: Visualizations use synthetic data. Case studies use hardcoded spot prices and rates from public sources (Yahoo Finance, FRED, EIA) with constructed futures prices to demonstrate model mechanics.

### Project Structure
```
fair-basis-arbitrage/
├── src/
│   ├── futures_pricer.py           # Core pricing engine (382 lines)
│   ├── historical_validation.py    # Illustrative case studies (224 lines)
│   └── create_visualizations.py    # Generate 7 portfolio charts (568 lines)
├── sample_demonstration.py         # Basic usage examples (103 lines)
├── visualizations/                 # Generated charts (7 PNG files, 300 DPI)
├── report/
│   └── Fair_Basis_Arbitrage_Report.tex  # LaTeX report (1,200+ lines)
└── README.md                       # This file
```

---

## Portfolio Visualizations

**7 charts** demonstrating strategy performance (generated from synthetic data):

| Chart | Description | Key Insight |
|-------|-------------|-------------|
| **1. Basis Deviation Time Series** | 60-day actual vs fair value | Visual proof of futures deviating from fair value |
| **2. No-Arbitrage Bounds** | Multi-asset snapshot | Shows which assets have exploitable arbitrage |
| **3. Sensitivity Heatmap** | Interest rate x dividend yield | 2D parameter sensitivity analysis |
| **4. Convenience Yield Term Structure** | Natural gas maturity curve | Illustrates why commodity arbitrage fails |
| **5. Transaction Cost Breakdown** | Feasibility by asset class | Currencies/equities arbitrageable, commodities not |
| **6. Signal Frequency Analysis** | Performance metrics table | **68-71% win rate for financial vs 12% for commodities** |
| **7. P&L Distribution** | S&P 500 histogram | 170 signals, 70.6% win rate, +90.7 bps cumulative |

**Generate charts**: `python src/create_visualizations.py` (output saved to `visualizations/`)

---

## Illustrative Case Studies

**3 examples** using hardcoded market parameters from 2022-2023. Spot prices and rates are sourced from public data (Yahoo Finance, FRED, EIA). Futures prices are constructed (fair value + a fixed deviation) to illustrate how the model detects and evaluates mispricings.

### Case Study 1: S&P 500 Cash-and-Carry (January 17, 2023)
- **Market Context**: Fed terminal rate regime (5% Fed Funds), index rebalancing flows
- **Deviation**: +$8.50 (+0.214%) above fair value
- **Signal**: SELL futures (cash-and-carry arbitrage)
- **Outcome**: +1.8 bps profit, convergence in 3 days
- **Why It Worked**: Financial asset, observable inputs, low transaction costs (7 bps)

### Case Study 2: Natural Gas Backwardation (March 7, 2022)
- **Market Context**: Russia-Ukraine war, extreme supply disruptions
- **Deviation**: $4.95 spot vs $4.25 futures (14.1% backwardation)
- **Implied Convenience Yield**: **58% (EXTREME)**
- **Outcome**: FAILED - Cannot short physical gas, rational scarcity pricing
- **Why It Failed**: Unobservable convenience yield, physical delivery constraints

### Case Study 3: EUR/USD CIP Arbitrage (October 12, 2023)
- **Market Context**: Fed 5.40% vs ECB 4.50% (90 bps differential)
- **Deviation**: +12 pips above covered interest parity
- **Signal**: CIP arbitrage (borrow USD, invest EUR, hedge with forward)
- **Outcome**: +1.8 bps profit, convergence in 24 hours
- **Why It Worked**: Pure financial, observable rates, ultra-low costs (1.5 pips)

---

## Signal Performance Analysis

Analyzed **12 months of simulated signal data (2023)** across 6 asset classes:

| Asset Class | Signals/Month | Win Rate | Avg Profit (bps) | Sharpe Ratio | Feasibility |
|-------------|---------------|----------|------------------|--------------|-------------|
| **S&P 500** | 3.2 | 68% | 1.2 | 2.1 | High |
| **NASDAQ-100** | 2.8 | 71% | 1.5 | 2.3 | High |
| **EUR/USD** | 5.7 | 71% | 0.8 | 1.8 | High |
| **GBP/USD** | 4.3 | 69% | 0.9 | 1.6 | High |
| **Gold** | 1.2 | 45% | -0.3 | -0.2 | Low |
| **Natural Gas** | 8.1 | **12%** | **-2.1** | **-0.8** | **Infeasible** |

**Key Findings**:
- **Financial Assets**: 68-71% win rates, positive Sharpe ratios (1.6-2.3), rapid convergence
- **Commodities**: 12-45% win rates, negative Sharpe, deviations persist for months
- Natural gas generates most signals (8.1/month) but worst performance (12% win rate)

---

## Supported Asset Classes

**Commodities** (natural gas, oil, gold)
- Formula: F = S x e^((r + u - y)T)
- Includes convenience yield estimation (Newton-Raphson solver)
- **Result**: Arbitrage infeasible due to unobservable convenience yield

**Equity Indices** (S&P 500, NASDAQ)
- Formula: F = S x e^((r - q)T)
- Feasible arbitrage via ETFs (SPY, QQQ)
- **Result**: 68-71% win rate, 2.1-2.3 Sharpe ratio

**Currencies** (EUR/USD, major pairs)
- Formula: F = S x e^((r_d - r_f)T)
- Covered interest parity (CIP)
- **Result**: 71% win rate, 1.8 Sharpe ratio

**Individual Stocks** & **Cryptocurrencies**
- Framework ready for extension

---

## Cost-of-Carry Model

The fundamental relationship:

```
F* = S x e^(cost_of_carry x T)
```

Where cost of carry depends on asset type:

| Asset | Cost of Carry | Components |
|-------|---------------|------------|
| Commodity | r + u - y | financing + storage - convenience yield |
| Equity Index | r - q | financing - dividend yield |
| Currency | r_d - r_f | domestic rate - foreign rate |

Variables:
- S = Current spot price
- F* = Fair (theoretical) futures price
- r = Risk-free rate (SOFR)
- u = Storage cost rate
- y = Convenience yield
- q = Dividend yield
- T = Time to expiration (years)

---

## Technical Implementation

### Technology Stack

| Library | Purpose |
|---------|---------|
| `numpy` | Numerical computation, exponential calculations |
| `pandas` | Time series data handling |
| `scipy` | Newton-Raphson solver for convenience yield |
| `matplotlib` & `seaborn` | Visualization generation |
| `yfinance` | Historical spot and futures prices |

### Code Architecture

**Object-Oriented Design** with specialized calculators:

1. **`futures_pricer.py` (382 lines)**:
   - Abstract base class `FairValueCalculator`
   - `CommodityCalculator`: Newton-Raphson convenience yield solver
   - `EquityIndexCalculator`: Cash-and-carry with dividend yield
   - `CurrencyCalculator`: Covered interest parity

2. **`historical_validation.py` (224 lines)**:
   - 3 illustrative case studies with hardcoded market parameters
   - Spot prices/rates from public sources; futures prices constructed to demonstrate model

3. **`create_visualizations.py` (568 lines)**:
   - 7 charts at 300 DPI
   - Styled with seaborn

---

## Why Commodity Arbitrage Fails

**Financial assets (equities, currencies):**
- Easy to short
- Observable inputs (SOFR, dividend yields, central bank rates)
- High liquidity, low transaction costs
- Cash settlement
- **Arbitrage is feasible** (68-71% win rate in simulated analysis)

**Physical commodities:**
- Cannot short physical inventory
- **Unobservable convenience yield** (must be reverse-engineered)
- Delivery logistics (location, quality, timing)
- Physical settlement required
- **Arbitrage is nearly impossible** (12% win rate, 97% false positives in simulated analysis)

**Key Insight**: What appears as "mispricing" in commodities often reflects rational scarcity pricing, not arbitrage opportunity.

---

## Usage Examples

### Basic Fair Value Calculation
```python
from src.futures_pricer import EquityIndexCalculator, AssetParameters

# S&P 500 example
params = AssetParameters(
    spot_price=4500.00,
    futures_price=4525.00,
    time_to_expiry=90/365,
    risk_free_rate=0.05,
    dividend_yield=0.015,
    asset_type="equity_index"
)

calculator = EquityIndexCalculator()
fair_value = calculator.calculate_fair_futures(params)
deviation = params.futures_price - fair_value

print(f"Fair Value: ${fair_value:.2f}")
print(f"Deviation: ${deviation:.2f} ({deviation/fair_value*100:.2f}%)")
```

### Run Sample Demonstration
```bash
python sample_demonstration.py
```

Shows:
- Natural gas analysis (contango and backwardation scenarios)
- S&P 500 futures fair value
- EUR/USD forward pricing

---

## Documentation

### LaTeX Report

A full academic report (`report/Fair_Basis_Arbitrage_Report.tex`, 1,200+ lines) covering:

- **Section 1**: Executive Summary with project highlights
- **Section 2**: Cost-of-carry framework and mathematical derivations
- **Section 3**: Literature review (Geman 2005, Hull 2021)
- **Section 4**: Methodology and implementation
- **Section 5**: Results
  - 3 illustrative case studies
  - Signal performance analysis
- **Section 6**: Why Commodity Arbitrage Fails
- **Section 7**: Conclusion and applications

**Compile with LaTeX** for PDF output.

---

### Key Metrics
- **68-71%** - Financial asset arbitrage win rate (simulated)
- **3%** - Commodity signal success rate (97% false positives)
- **2.3 days** - S&P 500 mean reversion time (vs 47 days for natural gas)

---

## Author

**Zaid Annigeri**
- Master of Quantitative Finance, Rutgers Business School
- GitHub: [@Zaid282802](https://github.com/Zaid282802)
- LinkedIn: [Zaid Annigeri](https://www.linkedin.com/in/zed228)

---

## License

This project is available for educational and research purposes. Please provide attribution if used in academic work or presentations.

**Citation:**
```
Annigeri, Z. (2026). Fair Basis Arbitrage Indicator: Multi-Asset Derivatives Pricing
and Arbitrage Signal Generation. Master of Quantitative Finance Program,
Rutgers Business School.
```
