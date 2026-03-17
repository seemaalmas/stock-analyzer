from fundamentals.ingestion.stock_price_ingest import fetch_single_symbol
from sqlalchemy import text
from database.engine import engine

def validate_and_activate_symbol(symbol, lookback="3y"):
    df = fetch_single_symbol(symbol, lookback)

    if df is None or df.empty or len(df) < 100:
        raise ValueError(f"No usable data for {symbol}")

    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE symbols_master
            SET is_active = TRUE,
                activated_on = NOW()
            WHERE symbol = :symbol
        """), {"symbol": symbol})

    return True
