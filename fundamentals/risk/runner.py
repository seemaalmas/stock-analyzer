from fundamentals.risk.auditor_risk import detect_auditor_risk
from fundamentals.risk.cashflow_risk import detect_cashflow_risk
from fundamentals.risk.dilution_risk import detect_dilution_risk
from fundamentals.risk.governance_risk import detect_governance_risk

def run_risk_detection(symbol):
    detect_auditor_risk(symbol)
    detect_cashflow_risk(symbol)
    detect_dilution_risk(symbol)
    detect_governance_risk(symbol)

    print(f"⚠️ Risk detection completed for {symbol}")
