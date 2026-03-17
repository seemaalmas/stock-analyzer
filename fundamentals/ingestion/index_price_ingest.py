import yfinance as yf
import pandas as pd
from sqlalchemy import text
from database.engine import engine

INDEX_MAP = {
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK"
}

def ingest_indices(period="2y"):
    for index_name, ticker in INDEX_MAP.items():
        print(f"📥 Downloading {index_name}")

        df = yf.download(
            ticker,
            period=period,
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if df.empty:
            print(f"❌ No data for {index_name}")
            continue

        # ----------------------------
        # 1️⃣ Normalize dataframe
        # ----------------------------
        df = df.reset_index()
        df = df[["Date", "Open", "High", "Low", "Close"]]
        df.columns = ["trade_date", "open", "high", "low", "close"]
        df["index_name"] = index_name

        # ----------------------------
        # 2️⃣ Compute date range
        # ----------------------------
        min_date = df["trade_date"].min()
        max_date = df["trade_date"].max()

        # ----------------------------
        # 3️⃣ DELETE existing rows
        # ----------------------------
        with engine.begin() as conn:
            conn.execute(
                text("""
                    DELETE FROM index_daily
                    WHERE index_name = :index_name
                      AND trade_date BETWEEN :start AND :end
                """),
                {
                    "index_name": index_name,
                    "start": min_date,
                    "end": max_date
                }
            )

        # ----------------------------
        # 4️⃣ INSERT fresh data
        # ----------------------------
        df.to_sql(
            "index_daily",
            engine,
            if_exists="append",
            index=False,
            method="multi"
        )

        print(
            f"✅ {index_name}: {len(df)} rows "
            f"({min_date.date()} → {max_date.date()})"
        )

if __name__ == "__main__":
    ingest_indices()
