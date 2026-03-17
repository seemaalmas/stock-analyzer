import pandas as pd
from database.engine import engine

def calculate_ema(symbol):
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

    if len(df) < 200:
        return None

    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["ema200"] = df["close"].ewm(span=200, adjust=False).mean()

    latest = df.iloc[-1]

    if latest.ema20 > latest.ema50 > latest.ema200:
        trend = "BULLISH"
    elif latest.ema20 < latest.ema50 < latest.ema200:
        trend = "BEARISH"
    else:
        trend = "NEUTRAL"

    return {
        "ema20": float(latest.ema20),
        "ema50": float(latest.ema50),
        "ema200": float(latest.ema200),
        "ema_trend": trend,
        "as_of_date": latest.trade_date
    }
