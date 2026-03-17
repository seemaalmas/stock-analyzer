import pandas as pd
from database.connection import get_connection, engine

def detect_price_structure(symbol, lookback=20):
    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT trade_date, high, low
        FROM price_daily
        WHERE symbol = %s
        ORDER BY trade_date
        """,
        conn,
        params=(symbol,)
    )

    conn.close()

    if df.empty or len(df) < lookback:
        return None  # IMPORTANT

    df = df.tail(lookback)

    prev_high, curr_high = df["high"].iloc[-2], df["high"].iloc[-1]
    prev_low, curr_low = df["low"].iloc[-2], df["low"].iloc[-1]

    if curr_high > prev_high and curr_low > prev_low:
        structure, trend = "HH_HL", "UP"
    elif curr_high < prev_high and curr_low < prev_low:
        structure, trend = "LH_LL", "DOWN"
    else:
        structure, trend = "RANGE", "SIDEWAYS"

    return {
        "symbol": symbol,          # 🔥 THIS WAS MISSING
        "structure": structure,
        "trend": trend,
        "support": float(df["low"].min()),
        "resistance": float(df["high"].max())
    }

