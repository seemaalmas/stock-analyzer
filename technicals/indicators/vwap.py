import pandas as pd
from database.engine import engine

def calculate_vwap(symbol):
    df = pd.read_sql(
        """
        SELECT trade_date, close, volume
        FROM price_daily
        WHERE symbol = %(symbol)s
        ORDER BY trade_date
        """,
        engine,
        params={"symbol": symbol}
    )

    if len(df) < 20:
        return None

    df["cum_vol"] = df["volume"].cumsum()
    df["cum_vp"] = (df["close"] * df["volume"]).cumsum()
    df["vwap"] = df["cum_vp"] / df["cum_vol"]

    latest = df.iloc[-1]

    state = (
        "ABOVE_VWAP" if latest.close > latest.vwap
        else "BELOW_VWAP"
    )

    return {
        "vwap": float(latest.vwap),
        "vwap_state": state
    }
