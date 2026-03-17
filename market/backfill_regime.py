import pandas as pd
from database.engine import engine
from market.batch_runner import run_market_regime


def backfill_market_regime(start_date, end_date):
    dates_df = pd.read_sql(
        """
        SELECT DISTINCT trade_date
        FROM price_daily
        WHERE trade_date BETWEEN %s AND %s
        ORDER BY trade_date
        """,
        engine,
        params=(start_date, end_date)
    )

    print(f"🔁 Backfilling regime for {len(dates_df)} days")

    for trade_date in dates_df["trade_date"]:
        try:
            run_market_regime(trade_date)
        except Exception as e:
            print(f"❌ {trade_date}: {e}")

    print("✅ Market regime backfill completed")


if __name__ == "__main__":
    backfill_market_regime("2024-01-01", "2025-01-09")
