import numpy as np
import pandas as pd
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

class AssetType(Enum):
    COMMODITY = "commodity"
    EQUITY_INDEX = "equity_index"
    INDIVIDUAL_STOCK = "stock"
    CURRENCY = "currency"
    CRYPTOCURRENCY = "crypto"

class MarketStructure(Enum):
    CONTANGO = "contango"
    BACKWARDATION = "backwardation"
    FLAT = "flat"

class ArbitrageSignal(Enum):
    CASH_AND_CARRY = "cash_and_carry"
    REVERSE_CASH_AND_CARRY = "reverse_cash_carry"
    NO_ARBITRAGE = "no_arbitrage"

@dataclass
class AssetParameters:
    spot_price: float
    futures_price: float
    time_to_expiry: float
    risk_free_rate: float

    dividend_yield: float = 0.0
    foreign_rate: float = 0.0
    storage_cost_rate: float = 0.0
    convenience_yield: float = 0.0

    spot_transaction_cost: float = 0.001
    futures_transaction_cost: float = 0.0005

    asset_name: str = "Unknown"
    asset_type: AssetType = AssetType.COMMODITY
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.spot_price <= 0 or self.futures_price <= 0:
            raise ValueError("Prices must be positive")
        if self.time_to_expiry <= 0:
            raise ValueError("Time to expiry must be positive")

@dataclass
class FairBasisResult:
    asset_name: str
    asset_type: AssetType
    spot_price: float
    actual_futures: float
    time_to_expiry: float

    fair_futures: float
    cost_of_carry: float
    cost_of_carry_components: dict

    actual_basis: float
    fair_basis: float
    basis_deviation: float
    basis_deviation_pct: float

    upper_bound: float
    lower_bound: float
    total_transaction_cost: float

    signal: ArbitrageSignal
    market_structure: MarketStructure
    arbitrage_profit: float
    arbitrage_profit_pct: float
    annualized_return: float

    implied_convenience_yield: float
    timestamp: datetime

    def to_dict(self):
        return {
            'asset_name': self.asset_name,
            'asset_type': self.asset_type.value,
            'spot_price': self.spot_price,
            'actual_futures': self.actual_futures,
            'fair_futures': self.fair_futures,
            'basis_deviation_pct': self.basis_deviation_pct,
            'signal': self.signal.value,
            'market_structure': self.market_structure.value,
            'timestamp': self.timestamp
        }

class FairValueCalculator(ABC):

    @abstractmethod
    def calculate_fair_futures(self, params):
        pass

    @abstractmethod
    def get_cost_of_carry(self, params):
        pass

    def calculate(self, params):
        # Calculate fair futures price
        fair_futures = self.calculate_fair_futures(params)
        cost_of_carry, coc_components = self.get_cost_of_carry(params)

        # Calculate basis
        actual_basis = params.spot_price - params.futures_price
        fair_basis = params.spot_price - fair_futures
        basis_deviation = params.futures_price - fair_futures
        basis_deviation_pct = (basis_deviation / params.spot_price) * 100

        # Transaction costs
        spot_tc = params.spot_price * params.spot_transaction_cost * 2
        futures_tc = params.futures_price * params.futures_transaction_cost * 2
        total_tc = spot_tc + futures_tc

        # No-arbitrage bounds
        upper_bound = fair_futures + total_tc
        lower_bound = fair_futures - total_tc

        # Determine signal
        if params.futures_price > upper_bound:
            signal = ArbitrageSignal.CASH_AND_CARRY
            arb_profit = params.futures_price - fair_futures - total_tc
        elif params.futures_price < lower_bound:
            signal = ArbitrageSignal.REVERSE_CASH_AND_CARRY
            arb_profit = fair_futures - params.futures_price - total_tc
        else:
            signal = ArbitrageSignal.NO_ARBITRAGE
            arb_profit = 0.0

        arb_profit_pct = (arb_profit / params.spot_price) * 100
        annual_return = (arb_profit / params.spot_price) / params.time_to_expiry * 100

        # Market structure
        if fair_futures > params.spot_price * 1.001:
            market_structure = MarketStructure.CONTANGO
        elif fair_futures < params.spot_price * 0.999:
            market_structure = MarketStructure.BACKWARDATION
        else:
            market_structure = MarketStructure.FLAT

        # Implied convenience yield for commodities
        if params.asset_type == AssetType.COMMODITY:
            implied_y = self._calculate_implied_convenience_yield(params, fair_futures)
        else:
            implied_y = 0.0

        return FairBasisResult(
            asset_name=params.asset_name,
            asset_type=params.asset_type,
            spot_price=params.spot_price,
            actual_futures=params.futures_price,
            time_to_expiry=params.time_to_expiry,
            fair_futures=fair_futures,
            cost_of_carry=cost_of_carry,
            cost_of_carry_components=coc_components,
            actual_basis=actual_basis,
            fair_basis=fair_basis,
            basis_deviation=basis_deviation,
            basis_deviation_pct=basis_deviation_pct,
            upper_bound=upper_bound,
            lower_bound=lower_bound,
            total_transaction_cost=total_tc,
            signal=signal,
            market_structure=market_structure,
            arbitrage_profit=arb_profit,
            arbitrage_profit_pct=arb_profit_pct,
            annualized_return=annual_return,
            implied_convenience_yield=implied_y,
            timestamp=params.timestamp
        )

    def _calculate_implied_convenience_yield(self, params, fair_futures):
        # y = r + u - (1/T) * ln(F/S)
        if params.time_to_expiry > 0 and params.spot_price > 0:
            implied_y = (params.risk_free_rate + params.storage_cost_rate -
                        (1 / params.time_to_expiry) * np.log(params.futures_price / params.spot_price))
            return implied_y
        return 0.0

class CommodityCalculator(FairValueCalculator):

    def calculate_fair_futures(self, params):
        # F = S * e^((r + u - y) * T)
        r = params.risk_free_rate
        u = params.storage_cost_rate
        y = params.convenience_yield
        T = params.time_to_expiry
        S = params.spot_price

        fair_futures = S * np.exp((r + u - y) * T)
        return fair_futures

    def get_cost_of_carry(self, params):
        coc = params.risk_free_rate + params.storage_cost_rate - params.convenience_yield
        components = {
            'financing': params.risk_free_rate,
            'storage': params.storage_cost_rate,
            'convenience_yield': -params.convenience_yield,
            'total': coc
        }
        return coc, components

class EquityIndexCalculator(FairValueCalculator):

    def calculate_fair_futures(self, params):
        # F = S * e^((r - q) * T)
        r = params.risk_free_rate
        q = params.dividend_yield
        T = params.time_to_expiry
        S = params.spot_price

        fair_futures = S * np.exp((r - q) * T)
        return fair_futures

    def get_cost_of_carry(self, params):
        coc = params.risk_free_rate - params.dividend_yield
        components = {
            'financing': params.risk_free_rate,
            'dividend_yield': -params.dividend_yield,
            'total': coc
        }
        return coc, components

class CurrencyCalculator(FairValueCalculator):

    def calculate_fair_futures(self, params):
        # F = S * e^((r_d - r_f) * T)
        r_d = params.risk_free_rate
        r_f = params.foreign_rate
        T = params.time_to_expiry
        S = params.spot_price

        fair_futures = S * np.exp((r_d - r_f) * T)
        return fair_futures

    def get_cost_of_carry(self, params):
        coc = params.risk_free_rate - params.foreign_rate
        components = {
            'domestic_rate': params.risk_free_rate,
            'foreign_rate': -params.foreign_rate,
            'total': coc
        }
        return coc, components

class IndividualStockCalculator(FairValueCalculator):

    def calculate_fair_futures(self, params):
        # Similar to equity index but may have different repo rate
        r = params.risk_free_rate
        q = params.dividend_yield
        T = params.time_to_expiry
        S = params.spot_price

        fair_futures = S * np.exp((r - q) * T)
        return fair_futures

    def get_cost_of_carry(self, params):
        coc = params.risk_free_rate - params.dividend_yield
        components = {
            'financing': params.risk_free_rate,
            'dividend_yield': -params.dividend_yield,
            'total': coc
        }
        return coc, components

class CryptocurrencyCalculator(FairValueCalculator):

    def calculate_fair_futures(self, params):
        # F = S * e^(r * T)
        # Crypto has no dividends but may have staking yield
        r = params.risk_free_rate
        staking_yield = params.dividend_yield  # Reuse dividend_yield field
        T = params.time_to_expiry
        S = params.spot_price

        fair_futures = S * np.exp((r - staking_yield) * T)
        return fair_futures

    def get_cost_of_carry(self, params):
        coc = params.risk_free_rate - params.dividend_yield
        components = {
            'financing': params.risk_free_rate,
            'staking_yield': -params.dividend_yield,
            'total': coc
        }
        return coc, components

class FairBasisIndicator:

    def __init__(self):
        self.calculators = {
            AssetType.COMMODITY: CommodityCalculator(),
            AssetType.EQUITY_INDEX: EquityIndexCalculator(),
            AssetType.INDIVIDUAL_STOCK: IndividualStockCalculator(),
            AssetType.CURRENCY: CurrencyCalculator(),
            AssetType.CRYPTOCURRENCY: CryptocurrencyCalculator(),
        }
        self.history = []

    def calculate(self, params):
        calculator = self.calculators.get(params.asset_type)
        if not calculator:
            raise ValueError(f"Unsupported asset type: {params.asset_type}")

        result = calculator.calculate(params)
        self.history.append(result)
        return result

    def print_summary(self, result):
        print(f"FAIR BASIS ANALYSIS: {result.asset_name}")

        print(f"\nMarket Data:")
        print(f"  Spot Price:           ${result.spot_price:>12,.4f}")
        print(f"  Actual Futures:       ${result.actual_futures:>12,.4f}")
        print(f"  Fair Futures:         ${result.fair_futures:>12,.4f}")
        print(f"  Time to Expiry:       {result.time_to_expiry:>12.4f} years")

        print(f"\nCost of Carry:")
        for key, value in result.cost_of_carry_components.items():
            if key != 'total':
                print(f"  {key.replace('_', ' ').title():.<25} {value*100:>8.2f}%")
        print(f"  {'Total Cost of Carry':.<25} {result.cost_of_carry*100:>8.2f}%")

        print(f"\nBasis Analysis:")
        print(f"  Actual Basis:         ${result.actual_basis:>12,.4f}")
        print(f"  Fair Basis:           ${result.fair_basis:>12,.4f}")
        print(f"  Deviation:            ${result.basis_deviation:>12,.4f} ({result.basis_deviation_pct:+.3f}%)")

        print(f"\nNo-Arbitrage Bounds:")
        print(f"  Lower Bound:          ${result.lower_bound:>12,.4f}")
        print(f"  Fair Futures:         ${result.fair_futures:>12,.4f}")
        print(f"  Upper Bound:          ${result.upper_bound:>12,.4f}")
        print(f"  Transaction Cost:     ${result.total_transaction_cost:>12,.4f}")

        signal_symbols = {
            ArbitrageSignal.CASH_AND_CARRY: "SELL FUTURES (Overpriced)",
            ArbitrageSignal.REVERSE_CASH_AND_CARRY: "BUY FUTURES (Underpriced)",
            ArbitrageSignal.NO_ARBITRAGE: "NO ACTION (Fair Value)"
        }

        print(f"\nArbitrage Signal: {signal_symbols.get(result.signal, result.signal.value)}")
        print(f"  Market Structure:     {result.market_structure.value.upper()}")
        print(f"  Arbitrage Profit:     ${result.arbitrage_profit:>12,.4f} ({result.arbitrage_profit_pct:+.3f}%)")
        print(f"  Annualized Return:    {result.annualized_return:>12.2f}%")

        if result.asset_type == AssetType.COMMODITY:
            print(f"\nImplied Convenience Yield: {result.implied_convenience_yield*100:.2f}%")

    def clear_history(self):
        self.history = []

    def get_history_df(self):
        if not self.history:
            return pd.DataFrame()
        return pd.DataFrame([r.to_dict() for r in self.history])

if __name__ == "__main__":
    # Quick test
    indicator = FairBasisIndicator()

    # Test with natural gas
    params = AssetParameters(
        spot_price=2.50,
        futures_price=2.65,
        time_to_expiry=0.25,
        risk_free_rate=0.05,
        storage_cost_rate=0.06,
        convenience_yield=0.02,
        asset_name="Natural Gas",
        asset_type=AssetType.COMMODITY
    )

    result = indicator.calculate(params)
    indicator.print_summary(result)
