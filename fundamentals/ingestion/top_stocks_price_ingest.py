import yfinance as yf
import pandas as pd
from database.connection import get_connection


NIFTY_50 = [
    "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT",
    "AXISBANK", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV",
    "BPCL", "BHARTIARTL", "BRITANNIA", "CIPLA",
    "COALINDIA", "DIVISLAB", "DRREDDY", "EICHERMOT",
    "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE",
    "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK",
    "ITC", "INDUSINDBK", "INFY", "JSWSTEEL",
    "KOTAKBANK", "LT", "M&M", "MARUTI",
    "NTPC", "NESTLEIND", "ONGC", "POWERGRID",
    "RELIANCE", "SBILIFE", "SBIN", "SUNPHARMA",
    "TCS", "TATAMOTORS", "TATASTEEL", "TECHM",
    "TITAN", "ULTRACEMCO", "UPL", "WIPRO"
]

def ingest():
    conn = get_connection()
    cur = conn.cursor()

    for ticker in NIFTY_50:
        yahoo_symbol = f"{ticker}.NS"
        
        print(f"Downloading {ticker}")

        df = yf.download(yahoo_symbol, period="2y", interval="1d", progress=True)

        if df.empty:
            print(f"No data for {ticker}")
            continue

        # 🔥 FIX 1: flatten multi-index columns
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

        df.reset_index(inplace=True)

        # 🔥 FIX 2: convert Date once
        df["Date"] = pd.to_datetime(df["Date"]).dt.date

        symbol = ticker.replace(".NS", "")

        for _, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO price_daily
                (symbol, trade_date, open, high, low, close, volume)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (symbol, trade_date) DO NOTHING
                """,
                (
                    symbol,
                    row["Date"],          # scalar
                    float(row["Open"]),   # scalar
                    float(row["High"]),
                    float(row["Low"]),
                    float(row["Close"]),
                    int(row["Volume"]) if not pd.isna(row["Volume"]) else 0
                )
            )

        print(f"Inserted {len(df)} rows for {symbol}")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    ingest()
