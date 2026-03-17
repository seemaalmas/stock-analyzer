from sqlalchemy import text
from database.engine import engine
from datetime import date

def build_spread_daily(trade_date=None):
    if not trade_date:
        trade_date = date.today()

    print(f"📊 Building spread for {trade_date}")

    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO spread_daily (symbol, trade_date, spread_pct)
            SELECT
                symbol,
                trade_date,
                ((high - low) / NULLIF(close, 0)) * 100 AS spread_pct
            FROM price_daily
            WHERE trade_date = :dt
              AND high IS NOT NULL
              AND low IS NOT NULL
              AND close IS NOT NULL
            ON CONFLICT (symbol, trade_date)
            DO UPDATE SET
                spread_pct = EXCLUDED.spread_pct
        """), {"dt": trade_date})

    print(f"✅ Spread built for {trade_date}")

if __name__ == "__main__":
    build_spread_daily()
