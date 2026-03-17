from sqlalchemy import text
from database.engine import engine

def get_weekly_signals(trade_date):
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT
                    symbol,
                    strategy,
                    entry_above,
                    stop_loss,
                    confidence,
                    trade_date
                FROM weekly_trade_signals
                WHERE trade_date = :trade_date
            """),
            {"trade_date": trade_date}
        ).fetchall()

    return [
        {
            "symbol": r.symbol,
            "strategy": r.strategy,
            "entry_above": r.entry_above,
            "stop_loss": r.stop_loss,
            "confidence": r.confidence,
            "trade_date": r.trade_date
        }
        for r in rows
    ]
