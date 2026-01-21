import numpy as np  
import pandas as pd
from futures_pricer import (
    FairBasisIndicator,
    AssetParameters,
    AssetType
)

def demonstrate_natural_gas():
    print("\n" + "="*70)
    print("NATURAL GAS ANALYSIS")
    print("="*70)

    indicator = FairBasisIndicator()

    # Contango scenario
    print("\nScenario 1: Contango (Ample Supply)")
    print("-" * 50)

    params1 = AssetParameters(
        spot_price=2.50,
        futures_price=2.65,
        time_to_expiry=0.25,
        risk_free_rate=0.05,
        storage_cost_rate=0.06,
        convenience_yield=0.02,
        spot_transaction_cost=0.002,
        futures_transaction_cost=0.001,
        asset_name="Natural Gas (Contango)",
        asset_type=AssetType.COMMODITY
    )

    result1 = indicator.calculate(params1)
    indicator.print_summary(result1)

    # Backwardation scenario
    print("\nScenario 2: Backwardation (Tight Supply)")
    print("-" * 50)

    params2 = AssetParameters(
        spot_price=4.50,
        futures_price=3.80,
        time_to_expiry=0.25,
        risk_free_rate=0.05,
        storage_cost_rate=0.06,
        convenience_yield=0.25,
        spot_transaction_cost=0.002,
        futures_transaction_cost=0.001,
        asset_name="Natural Gas (Backwardation)",
        asset_type=AssetType.COMMODITY
    )

    result2 = indicator.calculate(params2)
    indicator.print_summary(result2)

def demonstrate_sp500():
    print("\n" + "="*70)
    print("S&P 500 FUTURES ANALYSIS")
    print("="*70)

    indicator = FairBasisIndicator()

    params = AssetParameters(
        spot_price=4500,
        futures_price=4538,
        time_to_expiry=0.25,
        risk_free_rate=0.05,
        dividend_yield=0.015,
        spot_transaction_cost=0.0003,
        futures_transaction_cost=0.0001,
        asset_name="S&P 500",
        asset_type=AssetType.EQUITY_INDEX
    )

    result = indicator.calculate(params)
    indicator.print_summary(result)

def demonstrate_currency():
    print("\n" + "="*70)
    print("EUR/USD FORWARD ANALYSIS")
    print("="*70)

    indicator = FairBasisIndicator()

    params = AssetParameters(
        spot_price=1.10,
        futures_price=1.1055,
        time_to_expiry=0.5,
        risk_free_rate=0.05,
        foreign_rate=0.04,
        spot_transaction_cost=0.00005,
        futures_transaction_cost=0.00003,
        asset_name="EUR/USD",
        asset_type=AssetType.CURRENCY
    )

    result = indicator.calculate(params)
    indicator.print_summary(result)

def main():
    print("\n" + "="*70)
    print("FAIR BASIS INDICATOR - DEMONSTRATION")
    print("="*70)

    demonstrate_natural_gas()
    demonstrate_sp500()
    demonstrate_currency()

    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
