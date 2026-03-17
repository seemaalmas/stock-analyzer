import pandas as pd
from database.engine import engine

def calculate_breadth(trade_date):
    """
    Returns (advances, declines)
    """

    price_df = pd.read_sql(
        """
        SELECT symbol
        FROM price_daily
        WHERE trade_date = %s
        """,
        engine,
        params=(trade_date,)
    )

    if price_df.empty:
        return None, None

    tech_df = pd.read_sql(
        """
        SELECT symbol, ema_trend
        FROM technical_state
        """,
        engine
    )

    merged = price_df.merge(tech_df, on="symbol", how="inner")

    advances = merged[
        merged["ema_trend"].isin(["BULLISH", "STRONG_BULLISH"])
    ].shape[0]

    declines = merged.shape[0] - advances

    return advances, declines
