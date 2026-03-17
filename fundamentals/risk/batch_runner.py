from fundamentals.risk.symbols import fetch_all_symbols
from fundamentals.risk.db_utils import clear_existing_flags
from fundamentals.risk.auditor_risk import detect_auditor_risk
from fundamentals.risk.cashflow_risk import detect_cashflow_risk
from fundamentals.risk.dilution_risk import detect_dilution_risk
from fundamentals.risk.governance_risk import detect_governance_risk

def run_batch_risk_detection():
    symbols = fetch_all_symbols()

    print(f"🔍 Running risk detection for {len(symbols)} stocks")

    for symbol in symbols:
        try:
            clear_existing_flags(symbol)

            detect_auditor_risk(symbol)
            detect_cashflow_risk(symbol)
            detect_dilution_risk(symbol)
            detect_governance_risk(symbol)

            print(f"✅ Completed risk checks: {symbol}")

        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")

    print("🎯 Step-1.3 batch risk detection completed")
