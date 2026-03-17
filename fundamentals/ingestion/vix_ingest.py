import yfinance as yf
import pandas as pd
from sqlalchemy import text
from database.engine import engine

def ingest_vix(period="2y"):
    df = yf.download(
        "^INDIAVIX",
        period=period,
        interval="1d",
        progress=False,
        auto_adjust=True
    )

    if df.empty:
        print("❌ No VIX data")
        return

    df = df.reset_index()
    df = df[["Date", "Close"]]
    df.columns = ["trade_date", "vix"]

    min_date = df["trade_date"].min()
    max_date = df["trade_date"].max()

    # 🔥 DELETE FIRST
    with engine.begin() as conn:
        conn.execute(
            text("""
                DELETE FROM vix_daily
                WHERE trade_date BETWEEN :start AND :end
            """),
            {"start": min_date, "end": max_date}
        )

    # ✅ INSERT CLEAN
    df.to_sql(
        "vix_daily",
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    print(f"✅ VIX inserted: {len(df)} rows ({min_date.date()} → {max_date.date()})")

if __name__ == "__main__":
    ingest_vix()
