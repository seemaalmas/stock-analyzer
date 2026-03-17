from sqlalchemy import text
from database.engine import engine
from datetime import date

def build_liquidity_daily(trade_date=None):
    if not trade_date:
        trade_date = date.today()

    print(f"📊 Building liquidity for {trade_date}")

    with engine.begin() as conn:
        # delete first (idempotent)
        conn.execute(
            text("""
                DELETE FROM liquidity_daily
                WHERE trade_date = :dt
            """),
            {"dt": trade_date}
        )

        # insert ONLY for this date
        result = conn.execute(
            text("""
                INSERT INTO liquidity_daily (trade_date, symbol, avg_volume)
                SELECT
                    trade_date,
                    symbol,
                    AVG(volume) AS avg_volume
                FROM price_daily
                WHERE trade_date = :dt
                GROUP BY trade_date, symbol
            """),
            {"dt": trade_date}
        )

    print(f"✅ Liquidity built for {trade_date}")

if __name__ == "__main__":
    build_liquidity_daily()
