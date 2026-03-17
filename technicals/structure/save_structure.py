from database.connection import get_connection
from technicals.structure.price_structure import detect_price_structure

def save_structure(symbol):
    data = detect_price_structure(symbol)

    if data is None:
        print(f"⚠️ Skipping structure save for {symbol}")
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO price_structure
        (symbol, structure, trend, support, resistance)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (symbol)
        DO UPDATE SET
            structure = EXCLUDED.structure,
            trend = EXCLUDED.trend,
            support = EXCLUDED.support,
            resistance = EXCLUDED.resistance,
            detected_on = CURRENT_DATE
        """,
        (
            data["symbol"],
            data["structure"],
            data["trend"],
            data["support"],
            data["resistance"]
        )
    )

    conn.commit()
    cur.close()
    conn.close()
