from datetime import date
import pandas as pd
from sqlalchemy import text
from database.engine import engine
from market.index_trend import get_index_trend
from market.vix import get_vix
from market.breadth import calculate_breadth
from market.classifier import classify_regime
from market.regime_engine import classify_market_regime


def get_latest_common_trade_date():
    df = pd.read_sql(
        """
        SELECT
          (SELECT MAX(trade_date) FROM price_daily) AS price_dt,
          (SELECT MAX(trade_date) FROM index_daily) AS index_dt,
          (SELECT MAX(trade_date) FROM vix_daily) AS vix_dt
        """,
        engine
    )

    row = df.iloc[0]

    dates = [
        row["price_dt"],
        row["index_dt"],
        row["vix_dt"]
    ]

    # Remove NULL / None values
    valid_dates = [d for d in dates if d is not None]

    if len(valid_dates) < 3:
        raise RuntimeError(
            f"❌ Missing data for regime calculation: {dates}"
        )

    return min(valid_dates)

def save_regime(trade_date, regime, nifty_trend, bank_trend, breadth_ratio, vix):
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO market_regime
                (trade_date, regime, nifty_trend, banknifty_trend, breadth_ratio, vix)
                VALUES (:trade_date, :regime, :nifty_trend, :bank_trend, :breadth_ratio, :vix)
                ON CONFLICT (trade_date)
                DO UPDATE SET
                    regime = EXCLUDED.regime,
                    nifty_trend = EXCLUDED.nifty_trend,
                    banknifty_trend = EXCLUDED.banknifty_trend,
                    breadth_ratio = EXCLUDED.breadth_ratio,
                    vix = EXCLUDED.vix
            """),
            {
                "trade_date": trade_date,
                "regime": regime,
                "nifty_trend": nifty_trend,
                "bank_trend": bank_trend,
                "breadth_ratio": breadth_ratio,
                "vix": vix
            }
        )

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


def run_market_regime(trade_date=None):
    if not trade_date:
        trade_date = get_latest_trade_date()

    with engine.connect() as conn:
        data = conn.execute(text("""
            SELECT
                ni.trend AS nifty_trend,
                bi.trend AS bank_trend,
                mb.advance_decline_ratio,
                v.vix,
                ni.gap_pct
            FROM index_state ni
            JOIN index_state bi ON bi.index_name = 'BANKNIFTY'
            JOIN market_breadth_daily mb ON mb.trade_date = ni.trade_date
            JOIN vix_daily v ON v.trade_date = ni.trade_date
            WHERE ni.index_name = 'NIFTY'
              AND ni.trade_date = :dt
        """), {"dt": trade_date}).fetchone()

    if not data:
        print("❌ Missing data for regime")
        return

    regime = classify_market_regime(
        data.nifty_trend,
        data.bank_trend,
        data.advance_decline_ratio,
        data.vix,
        data.gap_pct
    )

    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO market_regime
            (trade_date, regime, nifty_trend, banknifty_trend, ad_ratio, vix, gap_pct)
            VALUES
            (:dt, :regime, :nt, :bt, :ad, :vix, :gap)
            ON CONFLICT (trade_date) DO UPDATE
            SET regime = EXCLUDED.regime
        """), {
            "dt": trade_date,
            "regime": regime,
            "nt": data.nifty_trend,
            "bt": data.bank_trend,
            "ad": data.advance_decline_ratio,
            "vix": data.vix,
            "gap": data.gap_pct
        })

    print(f"📊 Market Regime on {trade_date}: {regime}")

if __name__ == "__main__":
    run_market_regime()
