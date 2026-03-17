from fundamentals.risk.symbols import fetch_all_symbols
from fundamentals.eligibility.engine import apply_trade_eligibility

def run_trade_eligibility():
    symbols = fetch_all_symbols()

    for symbol in symbols:
        apply_trade_eligibility(symbol)

    print("✅ Step-1.5 trade eligibility completed")
