import pandas as pd
from database.connection import get_connection

def ingest_price_csv(csv_path):
    df = pd.read_csv(csv_path)

    conn = get_connection()
    cur = conn.cursor()

    for _, row in df.iterrows():
        cur.execute(
            """
            INSERT INTO price_daily
            (symbol, trade_date, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, trade_date) DO NOTHING
            """,
            (
                row["SYMBOL"],
                row["TIMESTAMP"],
                row["OPEN"],
                row["HIGH"],
                row["LOW"],
                row["CLOSE"],
                row["TOTTRDQTY"]
            )
        )

    conn.commit()
    cur.close()
    conn.close()
