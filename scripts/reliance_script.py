import yfinance as yf
import pandas as pd
from database.connection import get_connection

ticker = "RELIANCE.NS"
symbol = "RELIANCE"

df = yf.download(ticker, period="6mo", interval="1d")
df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
df.reset_index(inplace=True)
df["Date"] = pd.to_datetime(df["Date"]).dt.date

conn = get_connection()
cur = conn.cursor()

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
            row["Date"],
            float(row["Open"]),
            float(row["High"]),
            float(row["Low"]),
            float(row["Close"]),
            int(row["Volume"]) if not pd.isna(row["Volume"]) else 0
        )
    )

conn.commit()
cur.close()
conn.close()

print("✅ Inserted yfinance data for RELIANCE")
