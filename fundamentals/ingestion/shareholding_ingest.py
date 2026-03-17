import pandas as pd
from database.connection import get_connection

def ingest_shareholding(csv_path):
    df = pd.read_csv(csv_path)
    conn = get_connection()
    cur = conn.cursor()

    for _, row in df.iterrows():
        cur.execute(
            """
            INSERT INTO shareholding_raw
            (symbol, quarter, promoter_pct, fii_pct, dii_pct, pledged_pct)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                row["Symbol"],
                row["Quarter"],
                row["Promoter"],
                row["FII"],
                row["DII"],
                row["Pledged"]
            )
        )

    conn.commit()
    cur.close()
    conn.close()
