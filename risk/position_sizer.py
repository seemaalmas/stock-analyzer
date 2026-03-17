from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
MAX_RISK_PER_TRADE = os.getenv("MAX_RISK_PER_TRADE")

def calculate_quantity(capital, entry, stop):
    risk_per_trade = capital * MAX_RISK_PER_TRADE
    per_share_risk = abs(entry - stop)

    if per_share_risk == 0:
        return 0

    qty = risk_per_trade // per_share_risk
    return int(qty)
