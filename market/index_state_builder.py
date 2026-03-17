from sqlalchemy import text
from database.engine import engine
from datetime import date

def get_latest_trade_date():
    with engine.connect() as conn:
        return conn.execute(text("""
            SELECT MIN(dt)
            FROM (
                SELECT MAX(trade_date) AS dt FROM price_daily
                UNION ALL
                SELECT MAX(trade_date) FROM index_daily
                UNION ALL
                SELECT MAX(trade_date) FROM vix_daily
            ) x
        """)).scalar()


def build_index_state(trade_date=None):
    if not trade_date:
        trade_date = get_latest_trade_date()

    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT
                index_name,
                trade_date,
                close,
                LAG(close) OVER (PARTITION BY index_name ORDER BY trade_date) AS prev_close,
                open
            FROM index_daily
            WHERE trade_date <= :dt
        """), {"dt": trade_date}).fetchall()

        for r in rows:
            if not r.prev_close:
                continue

            trend = "UP" if r.close > r.prev_close else "DOWN"
            gap_pct = round(((r.open - r.prev_close) / r.prev_close) * 100, 2)

            conn.execute(text("""
                INSERT INTO index_state
                (index_name, trade_date, trend, gap_pct)
                VALUES (:idx, :dt, :trend, :gap)
                ON CONFLICT DO NOTHING
            """), {
                "idx": r.index_name,
                "dt": r.trade_date,
                "trend": trend,
                "gap": gap_pct
            })

    print("✅ index_state built")

if __name__ == "__main__":
    build_index_state()
