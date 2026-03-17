from sqlalchemy import text as sql_text
from database.engine import engine
from datetime import date

from strategies.weekly.breakout import is_weekly_breakout
from strategies.weekly.pullback import is_weekly_pullback


def run_weekly_scan(trade_date=None):
    if not trade_date:
        trade_date = date.today()

    results = []

    with engine.connect() as conn:
        symbols = conn.execute(
            sql_text("""
                SELECT symbol
                FROM symbols_master
                WHERE is_active = TRUE
            """)
        ).fetchall()

    for (symbol,) in symbols:

        breakout = is_weekly_breakout(symbol, trade_date)
        if breakout:
            results.append(breakout)
            print(f"✅ BREAKOUT: {symbol}")
            continue

        pullback = is_weekly_pullback(symbol, trade_date)
        if pullback:
            results.append(pullback)
            print(f"✅ PULLBACK: {symbol}")


    print(f"\n🎯 Weekly Candidates: {len(results)}")

    save_weekly_signals(results, trade_date)
    return results


def save_weekly_signals(signals, trade_date):
    with engine.begin() as conn:
        for s in signals:
            conn.execute(
                sql_text("""
                    INSERT INTO weekly_trade_signals
                    (symbol, strategy, entry_above, stop_loss, confidence, trade_date)
                    VALUES
                    (:symbol, :strategy, :entry_above, :stop_loss, :confidence, :trade_date)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "symbol": s["symbol"],
                    "strategy": s["strategy"],
                    "entry_above": s.get("entry_above"),
                    "stop_loss": s.get("stop_loss"),
                    "confidence": s.get("confidence", "MEDIUM"),
                    "trade_date": trade_date
                }
            )



if __name__ == "__main__":
    run_weekly_scan()
