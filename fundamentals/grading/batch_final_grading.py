from fundamentals.risk.symbols import fetch_all_symbols
from fundamentals.grading.final_grading import apply_risk_downgrades

def run_final_grading():
    symbols = fetch_all_symbols()

    for symbol in symbols:
        apply_risk_downgrades(symbol)

    print("✅ Step-1.4 final grading completed")
