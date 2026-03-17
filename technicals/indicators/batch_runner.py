from sqlalchemy import text
from database.engine import engine
from technicals.indicators.ema import calculate_ema
from technicals.indicators.rsi import calculate_rsi
from technicals.indicators.vwap import calculate_vwap

def run_indicator_batch():
    with engine.connect() as conn:
        symbols = conn.execute(
            text("""
                SELECT DISTINCT symbol
                FROM price_daily
            """)
        ).fetchall()

    for (symbol,) in symbols:
        ema = calculate_ema(symbol)
        rsi = calculate_rsi(symbol)
        vwap = calculate_vwap(symbol)

        if not ema or not rsi or not vwap:
            continue

        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO technical_state
                    (symbol, as_of_date,
                     ema20, ema50, ema200, ema_trend,
                     rsi, rsi_behavior,
                     vwap, vwap_state, updated_on)
                    VALUES
                    (:symbol, :as_of_date,
                     :ema20, :ema50, :ema200, :ema_trend,
                     :rsi, :rsi_behavior,
                     :vwap, :vwap_state, NOW())
                    ON CONFLICT (symbol, as_of_date)
                    DO UPDATE SET
                        ema20 = EXCLUDED.ema20,
                        ema50 = EXCLUDED.ema50,
                        ema200 = EXCLUDED.ema200,
                        ema_trend = EXCLUDED.ema_trend,
                        rsi = EXCLUDED.rsi,
                        rsi_behavior = EXCLUDED.rsi_behavior,
                        vwap = EXCLUDED.vwap,
                        vwap_state = EXCLUDED.vwap_state,
                        updated_on = NOW()
                """),
                {
                    "symbol": symbol,
                    **ema,
                    **rsi,
                    **vwap
                }
            )

        print(f"✅ Indicators updated for {symbol}")

    print("🎯 Indicator batch completed")

if __name__ == "__main__":
    run_indicator_batch()
