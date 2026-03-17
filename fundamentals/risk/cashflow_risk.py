from database.connection import engine
import pandas as pd
from datetime import date

def detect_cashflow_risk(symbol: str):
    df = pd.read_sql(
    """
    SELECT fiscal_year, operating_cash_flow
    FROM public.cashflow_annual_raw
    WHERE symbol = %(symbol)s
    ORDER BY fiscal_year;
    """,
    engine,
    params={"symbol": symbol}
)


    if df.empty:
        return

    if (df["operating_cash_flow"] < 0).sum() >= 2:
        with engine.begin() as conn:
            conn.execute(
                """
                INSERT INTO fundamental_risk_flags
                (symbol, flag, severity, detected_on)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    symbol,
                    "NEGATIVE_OCF_MULTIYEAR",
                    "HIGH",
                    date.today(),
                )
            )
