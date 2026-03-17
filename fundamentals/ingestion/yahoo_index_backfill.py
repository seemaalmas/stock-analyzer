import yfinance as yf
import pandas as pd
from database.engine import engine

INDEX_MAP = {
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK"
}

def backfill_indices(years=3):
    for index_name, ticker in INDEX_MAP.items():
        print(f"⬇️ Backfilling {index_name}")

        df = yf.download(
            ticker,
            period=f"{years}y",
            interval="1d",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            continue

        df = df.reset_index()
        df["index_name"] = index_name

        df = df[["index_name","Date","Open","High","Low","Close"]]
        df.columns = ["index_name","trade_date","open","high","low","close"]

        df.to_sql(
            "index_daily",
            engine,
            if_exists="append",
            index=False,
            method="multi"
        )

        print(f"✅ {index_name}: {len(df)} rows")

if __name__ == "__main__":
    backfill_indices(3)
