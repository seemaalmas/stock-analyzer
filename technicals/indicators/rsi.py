import pandas as pd
from database.engine import engine

def calculate_rsi(symbol, period=14):
    df = pd.read_sql(
        """
        SELECT trade_date, close
        FROM price_daily
        WHERE symbol = %(symbol)s
        ORDER BY trade_date
        """,
        engine,
        params={"symbol": symbol}
    )

    if len(df) < period + 5:
        return None

    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    latest_rsi = rsi.iloc[-1]

    if latest_rsi >= 60:
        behavior = "STRONG"
    elif latest_rsi <= 40:
        behavior = "WEAK"
    else:
        behavior = "NEUTRAL"

    return {
        "rsi": float(latest_rsi),
        "rsi_behavior": behavior
    }
