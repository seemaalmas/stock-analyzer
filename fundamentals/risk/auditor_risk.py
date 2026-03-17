import pandas as pd
from database.connection import get_connection, engine
from fundamentals.risk.db_utils import insert_risk_flag

def detect_auditor_risk(symbol):
    df = pd.read_sql(
        """
        SELECT event_type
        FROM auditor_events
        WHERE symbol = %s
        ORDER BY event_date DESC
        """,
        engine,
        params=(symbol,)
    )

    if df.empty:
        return

    flags = []

    for _, row in df.iterrows():
        if row["event_type"] == "AUDITOR_RESIGNED":
            flags.append({
                "symbol": symbol,
                "flag": "AUDITOR_RESIGNED",
                "severity": "HIGH"
            })

        elif row["event_type"] == "QUALIFIED_REPORT":
            flags.append({
                "symbol": symbol,
                "flag": "QUALIFIED_AUDIT",
                "severity": "HIGH"
            })

        elif row["event_type"] == "AUDITOR_CHANGED_FREQUENTLY":
            flags.append({
                "symbol": symbol,
                "flag": "AUDITOR_INSTABILITY",
                "severity": "MEDIUM"
            })

    if flags:
        insert_risk_flag(flags)

