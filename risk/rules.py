from dotenv import load_dotenv
import os
from sqlalchemy import text
from database.engine import engine
# Load environment variables from .env
load_dotenv()

# Fetch variables
MIN_RR = os.getenv("MIN_RR")
MIN_LIQUIDITY = 2_000_000        # avg daily volume
MAX_SPREAD_PCT = 1.5             # %
MIN_RR = 2.0                     # minimum risk:reward

def validate_risk(entry, stop, target):
    risk = entry - stop
    reward = target - entry

    if risk <= 0:
        return False

    rr = reward / risk
    return rr >= MIN_RR

def check_liquidity(signal):
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT avg_volume
            FROM liquidity_daily
            WHERE symbol = :sym
              AND trade_date = :dt
        """), {
            "sym": signal["symbol"],
            "dt": signal["trade_date"]
        }).fetchone()

    if not row or row.avg_volume is None:
        return False

    return row.avg_volume >= MIN_LIQUIDITY


def check_spread(signal):
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT spread_pct
            FROM spread_daily
            WHERE symbol = :sym
              AND trade_date = :dt
        """), {
            "sym": signal["symbol"],
            "dt": signal["trade_date"]
        }).fetchone()

    if not row or row.spread_pct is None:
        return False

    return row.spread_pct <= MAX_SPREAD_PCT


def check_rr(signal):
    entry = signal.get("entry")
    stop = signal.get("stop_loss")
    target = signal.get("target")

    if not entry or not stop or not target:
        return False

    risk = entry - stop
    reward = target - entry

    if risk <= 0:
        return False

    return (reward / risk) >= MIN_RR
