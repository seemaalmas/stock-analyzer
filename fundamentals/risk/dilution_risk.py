import pandas as pd
from database.connection import get_connection, engine
from fundamentals.risk.db_utils import insert_risk_flag

def detect_dilution_risk(symbol):
    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT shares_before, shares_after
        FROM equity_actions
        WHERE symbol = %s
        ORDER BY action_date DESC
        """,
        engine,
        params=(symbol,)
    )

    conn.close()

    if df.empty:
        return

    for _, row in df.iterrows():
        if row["shares_after"] > row["shares_before"]:
            insert_risk_flag(
                symbol,
                "EQUITY_DILUTION",
                "MEDIUM"
            )
