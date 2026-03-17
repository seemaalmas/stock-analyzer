import pandas as pd
from database.connection import get_connection, engine
from fundamentals.risk.db_utils import insert_risk_flag

def detect_governance_risk(symbol):
    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT event_type
        FROM governance_events
        WHERE symbol = %s
        """,
        engine,
        params=(symbol,)
    )

    conn.close()

    for _, row in df.iterrows():
        if row["event_type"] == "PROMOTER_SELLING":
            insert_risk_flag(
                symbol,
                "PROMOTER_SELLING",
                "HIGH"
            )

        if row["event_type"] == "HIGH_PLEDGE":
            insert_risk_flag(
                symbol,
                "HIGH_PLEDGE",
                "HIGH"
            )

        if row["event_type"] == "MANAGEMENT_EXIT":
            insert_risk_flag(
                symbol,
                "MANAGEMENT_EXIT",
                "MEDIUM"
            )

        if row["event_type"] == "REGULATORY_ACTION":
            insert_risk_flag(
                symbol,
                "REGULATORY_ACTION",
                "HIGH"
            )
