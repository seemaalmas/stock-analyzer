from database.connection import get_connection

def insert_risk_flag(symbol, flag, severity):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO fundamental_risk_flags (symbol, flag, severity)
        VALUES (%s, %s, %s)
        """,
        (symbol, flag, severity)
    )

    conn.commit()
    cur.close()
    conn.close()


def clear_existing_flags(symbol):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM fundamental_risk_flags WHERE symbol = %s",
        (symbol,)
    )

    conn.commit()
    cur.close()
    conn.close()
