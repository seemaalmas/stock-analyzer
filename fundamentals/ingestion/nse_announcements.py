import pandas as pd
from database.connection import get_connection

def ingest_governance_events(df):
    conn = get_connection()
    cur = conn.cursor()

    for _, row in df.iterrows():
        cur.execute(
            """
            INSERT INTO governance_events
            (symbol, event_type, event_date, details, source)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                row["symbol"],
                row["category"],
                row["date"],
                row["headline"],
                "NSE"
            )
        )

    conn.commit()
    cur.close()
    conn.close()
