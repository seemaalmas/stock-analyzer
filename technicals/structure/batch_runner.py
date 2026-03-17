from database.connection import get_connection
from technicals.structure.price_structure import detect_price_structure


def fetch_symbols():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT symbol
        FROM symbols_master
        WHERE exchange = 'NSE'
    """)
    symbols = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return symbols


def save_structure(data):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO price_structure
        (symbol, structure, trend, support, resistance, detected_on)
        VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
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


def run_batch_structure_detection():
    symbols = fetch_symbols()
    print(f"🔍 Running price structure detection for {len(symbols)} stocks")

    for symbol in symbols:
        try:
            data = detect_price_structure(symbol)

            if data is None:
                print(f"⚠️ {symbol}: insufficient data")
                continue

            save_structure(data)
            print(f"✅ {symbol}: {data['structure']} ({data['trend']})")

        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")



if __name__ == "__main__":
    run_batch_structure_detection()
