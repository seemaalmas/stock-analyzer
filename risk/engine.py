from sqlalchemy import text
from database.engine import engine
from risk.rules import check_liquidity, check_spread, check_rr
from risk.position_sizer import calculate_quantity
from risk.rejection_engine import reject_signal


def apply_risk_controls(signal, capital, trade_date):
    rejected, reason = reject_signal(signal)

    if rejected:
        with engine.begin() as conn:
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

        return None


    if not check_liquidity(signal):
        reject_signal(trade_date, signal, "LOW_LIQUIDITY")
        return None

    if not check_spread(signal):
        reject_signal(trade_date, signal, "WIDE_SPREAD")
        return None

    if not check_rr(signal):
        reject_signal(trade_date, signal, "RR_TOO_LOW")
        return None

    qty = calculate_quantity(signal, capital)
    if qty <= 0:
        reject_signal(trade_date, signal, "ZERO_QTY")
        return None

    signal["quantity"] = qty
    return signal


def reject_signal(trade_date, signal, reason):
    with engine.begin() as conn:
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
