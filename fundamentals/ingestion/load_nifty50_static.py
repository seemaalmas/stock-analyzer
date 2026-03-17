from database.connection import get_connection

NIFTY_50 = [
    "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT",
    "AXISBANK", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV",
    "BPCL", "BHARTIARTL", "BRITANNIA", "CIPLA",
    "COALINDIA", "DIVISLAB", "DRREDDY", "EICHERMOT",
    "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE",
    "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK",
    "ITC", "INDUSINDBK", "INFY", "JSWSTEEL",
    "KOTAKBANK", "LT", "M&M", "MARUTI",
    "NTPC", "NESTLEIND", "ONGC", "POWERGRID",
    "RELIANCE", "SBILIFE", "SBIN", "SUNPHARMA",
    "TCS", "TATAMOTORS", "TATASTEEL", "TECHM",
    "TITAN", "ULTRACEMCO", "UPL", "WIPRO"
]

def load_nifty50():
    conn = get_connection()
    cur = conn.cursor()

    for symbol in NIFTY_50:
        yahoo_symbol = f"{symbol}.NS"
        cur.execute(
            """
            INSERT INTO symbols_master (symbol, yahoo_symbol, exchange)
            VALUES (%s, %s, 'NSE')
            ON CONFLICT (symbol) DO NOTHING
            """,
            (symbol, yahoo_symbol)
        )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ NIFTY 50 symbols loaded into symbols_master")

if __name__ == "__main__":
    load_nifty50()
