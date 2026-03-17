from sqlalchemy import text
from database.engine import engine
from datetime import timedelta

TARGET_R_MULTIPLE = 2
MAX_HOLD_DAYS = 10

def run_backtest(start_date, end_date):
    with engine.connect() as conn:
        signals = conn.execute(
            text("""
                SELECT
                    ts.trade_date,
                    ts.symbol,
                    ts.strategy,
                    ts.score,
                    w.entry_above,
                    w.stop_loss
                FROM trade_scores ts
                JOIN weekly_trade_signals w
                ON ts.trade_date = w.trade_date
                AND ts.symbol = w.symbol
                AND ts.strategy = w.strategy
                WHERE ts.trade_date BETWEEN :start AND :end
            """),
            {"start": start_date, "end": end_date}
        ).fetchall()

    print(f"📊 Backtesting {len(signals)} trades")

    for row in signals:
        trade_date, symbol, strategy, score, entry_above, stop_loss = row

        # 1️⃣ Entry day = next trading day
        with engine.connect() as conn:
            entry = conn.execute(
                text("""
                    SELECT trade_date, open
                    FROM price_daily
                    WHERE symbol = :symbol
                    AND trade_date > :trade_date
                    ORDER BY trade_date
                    LIMIT 1
                """),
                {"symbol": symbol, "trade_date": trade_date}
            ).fetchone()

        if not entry:
            continue

        entry_date, entry_price = entry

        risk = entry_price - stop_loss
        target = entry_price + TARGET_R_MULTIPLE * risk

        # 2️⃣ Monitor next N days
        with engine.connect() as conn:
            prices = conn.execute(
                text("""
                    SELECT trade_date, high, low, close
                    FROM price_daily
                    WHERE symbol = :symbol
                    AND trade_date > :entry_date
                    AND trade_date <= :end_date
                    ORDER BY trade_date
                """),
                {
                    "symbol": symbol,
                    "entry_date": entry_date,
                    "end_date": entry_date + timedelta(days=MAX_HOLD_DAYS)
                }
            ).fetchall()

        exit_price = None
        exit_date = None
        outcome = "TIME_EXIT"

        for p_date, high, low, close in prices:
            if low <= stop_loss:
                exit_price = stop_loss
                exit_date = p_date
                outcome = "LOSS"
                break

            if high >= target:
                exit_price = target
                exit_date = p_date
                outcome = "WIN"
                break

        if not exit_price:
            exit_price = prices[-1][3]
            exit_date = prices[-1][0]

        pnl_pct = (exit_price - entry_price) / entry_price * 100
        holding_days = (exit_date - entry_date).days
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO backtest_trades
                    (trade_date, symbol, strategy, score,
                    entry_price, stop_loss,
                    exit_price, exit_date,
                    pnl_pct, outcome, holding_days)
                    VALUES
                    (:td, :sym, :str, :score,
                    :ep, :sl,
                    :xp, :xd,
                    :pnl, :out, :hold)
                """),
                {
                    "td": trade_date,
                    "sym": symbol,
                    "str": strategy,
                    "score": score,
                    "ep": entry_price,
                    "sl": stop_loss,
                    "xp": exit_price,
                    "xd": exit_date,
                    "pnl": pnl_pct,
                    "out": outcome,
                    "hold": holding_days
                }
            )

    print("✅ Backtest completed")
