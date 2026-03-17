from database.connection import get_connection

def save_risk_metrics(total, flags):
    high = sum(1 for f in flags if f == "HIGH")
    medium = sum(1 for f in flags if f == "MEDIUM")
    low = sum(1 for f in flags if f == "LOW")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO risk_run_metrics
        (total_symbols, flagged_symbols, high_severity_count,
         medium_severity_count, low_severity_count)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (total, len(flags), high, medium, low)
    )

    conn.commit()
    cur.close()
    conn.close()
