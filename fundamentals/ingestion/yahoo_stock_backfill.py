import yfinance as yf
import pandas as pd
from database.engine import engine

def backfill_stocks(years=3):
    symbols = pd.read_sql(
        """
        SELECT symbol, yahoo_symbol
        FROM symbols_master
        WHERE index_name NOT IN ('INDEX')
        """,
        engine
    )

    for _, row in symbols.iterrows():
        symbol = row["symbol"]
        ticker = row["yahoo_symbol"]

        print(f"⬇️ Backfilling {symbol}")

        df = yf.download(
            ticker,
            period=f"{years}y",
            interval="1d",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            print(f"❌ No data for {symbol}")
            continue

        df = df.reset_index()
        df["symbol"] = symbol
        df["source"] = "YAHOO"

        df = df[["symbol","Date","Open","High","Low","Close","Volume","source"]]
        df.columns = ["symbol","trade_date","open","high","low","close","volume","source"]

        df.to_sql(
            "price_daily",
            engine,
            if_exists="append",
            index=False,
            method="multi"
        )

        print(f"✅ {symbol}: {len(df)} rows")

    print("🎯 Stock historical backfill complete")

if __name__ == "__main__":
    backfill_stocks(3)
