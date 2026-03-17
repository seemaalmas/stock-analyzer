from sqlalchemy import text
from database.engine import engine
from datetime import timedelta

from risk.constants import (
    MIN_LIQUIDITY,
    MAX_SPREAD_PCT,
    MIN_RR,
    EVENT_LOOKAHEAD_DAYS
)

def reject_signal(signal):
    """
    Returns:
      (True, reason)  → rejected
      (False, None)   → accepted
    """

    trade_date = signal["trade_date"]
    symbol = signal["symbol"]

    with engine.connect() as conn:

        # 1️⃣ Liquidity Check
        liq = conn.execute(text("""
            SELECT avg_volume
            FROM liquidity_daily
            WHERE symbol = :sym
              AND trade_date = :dt
        """), {"sym": symbol, "dt": trade_date}).fetchone()

        if not liq or liq.avg_volume < MIN_LIQUIDITY:
            return True, "LOW_LIQUIDITY"

        # 2️⃣ Spread Check
        spr = conn.execute(text("""
            SELECT spread_pct
            FROM spread_daily
            WHERE symbol = :sym
              AND trade_date = :dt
        """), {"sym": symbol, "dt": trade_date}).fetchone()

        if not spr or spr.spread_pct > MAX_SPREAD_PCT:
            return True, "WIDE_SPREAD"

        # 3️⃣ Event Risk Check
        evt = conn.execute(text("""
            SELECT 1
            FROM governance_events
            WHERE symbol = :sym
              AND event_date BETWEEN :dt AND :dt2
            LIMIT 1
        """), {
            "sym": symbol,
            "dt": trade_date,
            "dt2": trade_date + timedelta(days=EVENT_LOOKAHEAD_DAYS)
        }).fetchone()

        if evt:
            return True, "EVENT_RISK"

    # 4️⃣ Risk Reward Check (NO DB)
    entry = signal["entry"]
    stop = signal["stop_loss"]
    target = signal["target"]

    risk = entry - stop
    reward = target - entry

    if risk <= 0 or (reward / risk) < MIN_RR:
        return True, "BAD_RR"

    return False, None
