import yfinance as yf
import pandas as pd
from sqlalchemy import text
from database.engine import engine
import yfinance as yf

def ingest_stock_prices(period="6mo"):
    symbols = get_active_stock_symbols()

    if not symbols:
        print("❌ No active STOCK symbols found")
        return

    for sym in symbols:
        ticker = f"{sym}.NS"
        print(f"⬇️ Downloading {sym}")

        try:
            df = yf.download(
                ticker,
                period=period,
                interval="1d",
                auto_adjust=True,
                progress=False
            )
        except Exception as e:
            print(f"❌ Yahoo error for {sym}: {e}")
            continue

        if df.empty:
            print(f"❌ No data for {sym}")
            continue

        df = df.reset_index()
        df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
        df.columns = ["trade_date", "open", "high", "low", "close", "volume"]
        df["symbol"] = sym

        min_dt = df.trade_date.min()
        max_dt = df.trade_date.max()

        with engine.begin() as conn:
            conn.execute(text("""
                DELETE FROM price_daily
                WHERE symbol = :sym
                  AND trade_date BETWEEN :s AND :e
            """), {"sym": sym, "s": min_dt, "e": max_dt})

        df.to_sql(
            "price_daily",
            engine,
            if_exists="append",
            index=False,
            method="multi"
        )

        print(f"✅ {sym}: {len(df)} rows")

def fetch_single_symbol(symbol, period="3y"):

    ticker = f"{symbol}.NS"

    df = yf.download(
        ticker,
        period=period,
        interval="1d",
        progress=False,
        auto_adjust=True
    )

    if df.empty:
        return None

    df = df.reset_index()
    df["symbol"] = symbol
    df = df[["Date", "symbol", "Open", "High", "Low", "Close", "Volume"]]
    df.columns = ["trade_date", "symbol", "open", "high", "low", "close", "volume"]

    return df

def ingest_single_symbol(symbol, period="3y"):
    df = fetch_single_symbol(symbol, period)
    if df is None:
        return False

    with engine.begin() as conn:
        conn.execute(text("""
            DELETE FROM price_daily
            WHERE symbol = :symbol
              AND trade_date BETWEEN :start AND :end
        """), {
            "symbol": symbol,
            "start": df.trade_date.min(),
            "end": df.trade_date.max()
        })

    df.to_sql(
        "price_daily",
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    return True

def get_active_stock_symbols():
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT symbol
            FROM symbols_master
            WHERE symbol_type = 'STOCK'
              AND is_active = TRUE
        """)).fetchall()

    return [r[0] for r in rows]


if __name__ == "__main__":
    ingest_stock_prices()
