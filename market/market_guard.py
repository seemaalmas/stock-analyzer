from sqlalchemy import text
from database.engine import engine

def is_trade_allowed(trade_date):
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT regime
            FROM market_regime
            WHERE trade_date = :dt
        """), {"dt": trade_date}).scalar()

    return r in ("TREND_DAY", "RANGE_DAY")
