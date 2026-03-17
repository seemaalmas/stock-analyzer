from sqlalchemy import text
from database.engine import engine
from datetime import date

print("🔥 RUNNING NEW BREADTH BUILDER 🔥")

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

def build_market_breadth_daily(trade_date=None):
    if not trade_date:
        trade_date = get_latest_trade_date()

    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT
                COUNT(*) FILTER (WHERE close > prev_close) AS advances,
                COUNT(*) FILTER (WHERE close < prev_close) AS declines
            FROM (
                SELECT
                    symbol,
                    trade_date,
                    close,
                    LAG(close) OVER (PARTITION BY symbol ORDER BY trade_date) AS prev_close
                FROM price_daily
                WHERE trade_date <= :dt
            ) t
            WHERE trade_date = :dt
              AND prev_close IS NOT NULL
        """), {"dt": trade_date}).fetchone()

    if not row or row.advances is None or row.declines is None:
        print("⚠️ Breadth not computable (no data)")
        return

    if row.declines == 0:
        ad_ratio = row.advances
    else:
        ad_ratio = row.advances / row.declines

    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO market_breadth_daily
            (trade_date, advances, declines, advance_decline_ratio)
            VALUES (:dt, :adv, :dec, :ratio)
            ON CONFLICT (trade_date) DO UPDATE
            SET
                advances = EXCLUDED.advances,
                declines = EXCLUDED.declines,
                advance_decline_ratio = EXCLUDED.advance_decline_ratio
        """), {
            "dt": trade_date,
            "adv": row.advances,
            "dec": row.declines,
            "ratio": ad_ratio
        })

    print(f"✅ Market breadth built for {trade_date} | A/D={row.advances}/{row.declines}")

if __name__ == "__main__":
    build_market_breadth_daily()
