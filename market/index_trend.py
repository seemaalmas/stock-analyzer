import pandas as pd
from database.engine import engine

def get_index_trend(index_name, lookback=50):
    """
    Determines index trend using EMA50 slope.
    Returns: UP / DOWN / SIDEWAYS
    """

    df = pd.read_sql(
        """
        SELECT trade_date, close
        FROM index_daily
        WHERE index_name = %s
        ORDER BY trade_date
        """,
        engine,
        params=(index_name,)
    )

    if len(df) < lookback:
        return "SIDEWAYS"

    df["ema50"] = df["close"].ewm(span=50).mean()

    recent = df.iloc[-5:]

    # EMA slope logic
    if recent["ema50"].iloc[-1] > recent["ema50"].iloc[0]:
        return "UP"
    elif recent["ema50"].iloc[-1] < recent["ema50"].iloc[0]:
        return "DOWN"
    else:
        return "SIDEWAYS"
