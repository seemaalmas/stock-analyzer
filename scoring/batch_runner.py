from sqlalchemy import text
from database.engine import engine
from scoring.signal_scoring import score_signal
from scoring.probability_mapper import map_score_to_probability
from scoring.get_signals import get_weekly_signals
from scoring.context_builder import build_context
from risk.rejection_engine import reject_signal
from decimal import Decimal

def run_scoring(trade_date=None):

    # 🔒 Always score latest available signals
    if not trade_date:
        with engine.connect() as conn:
            trade_date = conn.execute(
                text("SELECT MAX(trade_date) FROM weekly_trade_signals")
            ).scalar()

    if not trade_date:
        print("❌ No weekly signals found. Scoring skipped.")
        return

    print(f"📅 Scoring signals for trade_date = {trade_date}")

    signals = get_weekly_signals(trade_date)

    if not signals:
        print("⚠️ No signals to score.")
        return

    # ✅ Use BEGIN for writes
    with engine.begin() as conn:
        for signal in signals:

            entry = signal.get("entry_above")
            stop = signal.get("stop_loss")

            if entry is None or stop is None:
                print(f"⚠️ Skipping {signal['symbol']} — missing entry/stop")
                continue

            risk = entry - stop
            target = entry + (risk * Decimal("2.0"))

            # 🔴 STEP 8 — SIGNAL REJECTION
            rejected, reason = reject_signal({
                "trade_date": trade_date,
                "symbol": signal["symbol"],
                "strategy": signal["strategy"],
                "entry": signal.get("entry_above"),
                "stop_loss": signal.get("stop_loss"),
                "target": signal.get("entry_above") * Decimal("1.02")
            })

            if rejected:
                print(f"❌ REJECTED {signal['symbol']} | {reason}")

                conn.execute(text("""
                    INSERT INTO signal_rejections
                    (trade_date, symbol, strategy, reason)
                    VALUES (:dt, :sym, :strat, :reason)
                    ON CONFLICT DO NOTHING
                """), {
                    "dt": trade_date,
                    "sym": signal["symbol"],
                    "strat": signal["strategy"],
                    "reason": reason
                })

                continue


            # ✅ STEP 9 — SCORING
            context = build_context(signal, trade_date)
            score = score_signal(signal, context)

            print("\n--- SIGNAL ---")
            print(signal)
            print("--- CONTEXT ---")
            print(context)
            print("--- SCORE ---")
            print(score)

            if score is None:
                continue

            probability, confidence = map_score_to_probability(score)

            conn.execute(
                text("""
                    INSERT INTO trade_scores
                    (trade_date, symbol, strategy, score, probability, confidence)
                    VALUES
                    (:trade_date, :symbol, :strategy, :score, :probability, :confidence)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "trade_date": trade_date,
                    "symbol": signal["symbol"],
                    "strategy": signal["strategy"],
                    "score": score,
                    "probability": probability,
                    "confidence": confidence
                }
            )

    print("🎯 Phase-5 Scoring completed successfully")


if __name__ == "__main__":
    run_scoring()
