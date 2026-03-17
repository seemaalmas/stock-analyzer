from sqlalchemy import text
from database.engine import engine
from risk.engine import apply_risk_controls
from datetime import date
from risk.rejection_engine import reject_signal

def get_latest_trade_date():
    with engine.connect() as conn:
        return conn.execute(text("""
            SELECT MIN(dt)
            FROM (
                SELECT MAX(trade_date) AS dt FROM price_daily
                UNION ALL
                SELECT MAX(trade_date) FROM index_daily
                UNION ALL
                SELECT MAX(trade_date) FROM vix_daily
            ) x
        """)).scalar()

def run_risk_engine(trade_date=None, capital=100000):
    if not trade_date:
        trade_date = get_latest_trade_date()

    # 🔥 MUST BE begin(), NOT connect()
    with engine.begin() as conn:
        rows = conn.execute(
            text("""
                SELECT
                    ts.trade_date,
                    ts.symbol,
                    ts.strategy,
                    ts.entry_above AS entry,
                    ts.stop_loss,
                    sc.score,
                    sc.probability,
                    sc.confidence,
                    mr.regime
                FROM weekly_trade_signals ts
                JOIN trade_scores sc
                  ON ts.symbol = sc.symbol
                 AND ts.strategy = sc.strategy
                 AND ts.trade_date = sc.trade_date
                JOIN market_regime mr
                  ON ts.trade_date = mr.trade_date
            """)
        ).fetchall()

        print(f"🔍 Rows fetched: {len(rows)}")

        for r in rows:
            signal = dict(r)

            if signal["regime"] == "NO_TRADE":
                continue

            signal["target"] = signal["entry"] + (signal["entry"] - signal["stop_loss"]) * 2

            rejected, reason = reject_signal(signal)

            if rejected:
                print(f"❌ REJECTED {signal['symbol']} | {reason}")
                continue


            approved = apply_risk_controls(signal, capital)



            if not approved:
                continue

            print("✅ INSERTING APPROVED TRADE:", approved)
            

            conn.execute(
                text("""
                    INSERT INTO approved_trades
                    (trade_date, symbol, strategy, entry, stop_loss, target,
                     quantity, risk_reward, score, probability, confidence, market_regime)
                    VALUES
                    (:trade_date, :symbol, :strategy, :entry, :stop_loss, :target,
                     :quantity, :rr, :score, :prob, :conf, :regime)
                """),
                {
                    "trade_date": trade_date,
                    "symbol": approved["symbol"],
                    "strategy": approved["strategy"],
                    "entry": approved["entry"],
                    "stop_loss": approved["stop_loss"],
                    "target": approved["target"],
                    "quantity": approved["quantity"],
                    "rr": approved["target"] / (approved["entry"] - approved["stop_loss"]),
                    "score": signal["score"],
                    "prob": signal["probability"],
                    "conf": signal["confidence"],
                    "regime": signal["regime"]
                }
            )


    print("✅ Phase-6 Risk Engine completed")

if __name__ == "__main__":
    run_risk_engine()