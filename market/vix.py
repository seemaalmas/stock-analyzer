import pandas as pd
from database.engine import engine

def get_vix(trade_date):
    df = pd.read_sql(
        """
        SELECT vix
        FROM vix_daily
        WHERE trade_date = %s
        """,
        engine,
        params=(trade_date,)
    )

    if df.empty:
        return None

    return float(df.iloc[0]["vix"])
