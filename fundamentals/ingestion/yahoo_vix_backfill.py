import yfinance as yf
import pandas as pd
from database.engine import engine

def backfill_vix(years=3):
    df = yf.download(
        "^INDIAVIX",
        period=f"{years}y",
        interval="1d",
        auto_adjust=True,
        progress=False
    )

    if df.empty:
        print("❌ No VIX data")
        return

    df = df.reset_index()
    df = df[["Date","Close"]]
    df.columns = ["trade_date","vix"]

    df.to_sql(
        "vix_daily",
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    print(f"✅ VIX: {len(df)} rows")

if __name__ == "__main__":
    backfill_vix(3)
