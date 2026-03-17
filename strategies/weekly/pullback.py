from sqlalchemy import text
from database.engine import engine
from datetime import timedelta


def is_weekly_pullback(symbol: str, trade_date):
    """
    Returns dict if weekly pullback is valid, else None
    """

    with engine.connect() as conn:

        # -------------------------------------------------
        # 1️⃣ MARKET REGIME — MUST BE TREND
        # -------------------------------------------------
        regime = conn.execute(
            text("""
                SELECT market_regime
                FROM market_regime
                WHERE trade_date = :trade_date
            """),
            {"trade_date": trade_date}
        ).scalar()

        if regime != "TREND":
            return None

        # -------------------------------------------------
        # 2️⃣ FUNDAMENTAL ELIGIBILITY
        # -------------------------------------------------
        fund = conn.execute(
            text("""
                SELECT final_grade, allowed_trade_types
                FROM fundamental_grades_final
                WHERE symbol = :symbol
            """),
            {"symbol": symbol}
        ).fetchone()

        if not fund:
            return None

        grade, allowed = fund

        if grade not in ("STRONG", "AVERAGE"):
            return None

        if "weekly" not in allowed:
            return None

        # -------------------------------------------------
        # 3️⃣ STRUCTURE CHECK (HH_HL)
        # -------------------------------------------------
        structure = conn.execute(
            text("""
                SELECT structure_type, duration, last_swing_low
                FROM price_structure
                WHERE symbol = :symbol
                  AND as_of_date = :trade_date
            """),
            {"symbol": symbol, "trade_date": trade_date}
        ).fetchone()

        if not structure:
            return None

        structure_type, duration, last_swing_low = structure

        if structure_type != "HH_HL" or duration < 20:
            return None

        # -------------------------------------------------
        # 4️⃣ PRICE LOCATION (EMA ZONE)
        # -------------------------------------------------
        price = conn.execute(
            text("""
                SELECT close
                FROM price_daily
                WHERE symbol = :symbol
                  AND trade_date = :trade_date
            """),
            {"symbol": symbol, "trade_date": trade_date}
        ).scalar()

        if not price:
            return None

        indicators = conn.execute(
            text("""
                SELECT ema20, ema50, ema200, rsi, vwap, vwap_state
                FROM technical_state
                WHERE symbol = :symbol
                  AND as_of_date = :trade_date
            """),
            {"symbol": symbol, "trade_date": trade_date}
        ).fetchone()

        if not indicators:
            return None

        ema20, ema50, ema200, rsi, vwap, vwap_state = indicators

        # EMA alignment
        if not (ema20 > ema50 > ema200):
            return None

        # Pullback must be into EMA zone
        if not (ema50 <= price <= ema20):
            return None

        # Must not break last swing low
        if price < last_swing_low:
            return None

        # -------------------------------------------------
        # 5️⃣ RSI BEHAVIOR (COOLING, NOT WEAK)
        # -------------------------------------------------
        if not (45 <= rsi <= 60):
            return None

        # -------------------------------------------------
        # 6️⃣ VWAP CONFIRMATION
        # -------------------------------------------------
        if vwap_state == "BELOW_VWAP":
            return None

        # -------------------------------------------------
        # 7️⃣ VOLUME FILTER
        # -------------------------------------------------
        vol_data = conn.execute(
            text("""
                SELECT
                    AVG(volume) FILTER (
                        WHERE trade_date BETWEEN :start AND :mid
                    ) AS expansion_vol,
                    AVG(volume) FILTER (
                        WHERE trade_date BETWEEN :mid AND :end
                    ) AS pullback_vol
                FROM price_daily
                WHERE symbol = :symbol
            """),
            {
                "symbol": symbol,
                "start": trade_date - timedelta(days=15),
                "mid": trade_date - timedelta(days=5),
                "end": trade_date
            }
        ).fetchone()

        if not vol_data:
            return None

        expansion_vol, pullback_vol = vol_data

        if pullback_vol is None or expansion_vol is None:
            return None

        if pullback_vol > expansion_vol:
            return None

        # -------------------------------------------------
        # 8️⃣ NEWS FILTER (LAST 3 DAYS)
        # -------------------------------------------------
        neg_news = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM news_headlines
                WHERE symbol = :symbol
                  AND sentiment_label = 'NEGATIVE'
                  AND trade_date BETWEEN :start AND :end
            """),
            {
                "symbol": symbol,
                "start": trade_date - timedelta(days=3),
                "end": trade_date
            }
        ).scalar()

        if neg_news and neg_news > 0:
            return None

        # -------------------------------------------------
        # ✅ WEEKLY PULLBACK CONFIRMED
        # -------------------------------------------------
        return {
            "symbol": symbol,
            "strategy": "WEEKLY_PULLBACK",
            "entry_zone": f"{round(ema50,2)}–{round(ema20,2)}",
            "stop_loss": round(last_swing_low, 2),
            "confidence": "HIGH"
        }
