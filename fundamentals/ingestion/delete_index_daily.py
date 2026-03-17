from sqlalchemy import text
from database.engine import engine


min_date = df["trade_date"].min()
max_date = df["trade_date"].max()

with engine.begin() as conn:
    conn.execute(
        text("""
            DELETE FROM index_daily
            WHERE index_name = :index_name
              AND trade_date BETWEEN :start AND :end
        """),
        {
            "index_name": "NIFTY",
            "start": min_date,
            "end": max_date
        }
    )