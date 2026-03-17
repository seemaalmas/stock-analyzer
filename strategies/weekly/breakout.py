from sqlalchemy import text
from database.engine import engine
from datetime import timedelta


def is_weekly_breakout(symbol: str, trade_date):
    """
    Returns dict with breakout details if valid, else None
    """

    with engine.connect() as conn:

        # -------------------------------
        # 1️⃣ STRUCTURE CHECK (RANGE)
        # -------------------------------
        structure = conn.execute(
            text("""
                SELECT symbol, structure, trend, support, resistance, detected_on
                FROM price_structure
                WHERE symbol = :symbol
                  AND trade_date = :trade_date
            """),
            {"symbol": symbol, "trade_date": trade_date}
        ).fetchone()

        if not structure:
            return None

        structure_type, range_high, range_low, duration = structure

        if structure_type != "RANGE" or duration < 15:
            return None

        # -------------------------------
        # 2️⃣ PRICE BREAKOUT CHECK
        # -------------------------------
        price = conn.execute(
            text("""
                SELECT close, volume
                FROM price_daily
                WHERE symbol = :symbol
                  AND trade_date = :trade_date
            """),
            {"symbol": symbol, "trade_date": trade_date}
        ).fetchone()

        if not price:
            return None

        close_price, today_volume = price

        if close_price <= range_high:
            return None

        # -------------------------------
        # 3️⃣ VOLUME EXPANSION
        # -------------------------------
        avg_volume = conn.execute(
            text("""
                SELECT AVG(volume)
                FROM price_daily
                WHERE symbol = :symbol
                  AND trade_date BETWEEN :start AND :end
            """),
            {
                "symbol": symbol,
                "start": trade_date - timedelta(days=30),
                "end": trade_date - timedelta(days=1)
            }
        ).scalar()

        if not avg_volume or today_volume < 1.5 * avg_volume:
            return None

        # -------------------------------
        # 4️⃣ INDICATOR CONFIRMATION
        # -------------------------------
        indicators = conn.execute(
            text("""
                SELECT ema20, ema50, rsi, vwap_position
                FROM technical_state
                WHERE symbol = :symbol
                  AND trade_date = :trade_date
            """),
            {"symbol": symbol, "trade_date": trade_date}
        ).fetchone()

        if not indicators:
            return None

        ema20, ema50, rsi, vwap_pos = indicators

        if not (ema20 > ema50):
            return None

        if vwap_pos != "ABOVE_VWAP":
            return None

        if not (55 <= rsi <= 70):
            return None

        # -------------------------------
        # 5️⃣ FUNDAMENTAL ELIGIBILITY
        # -------------------------------
        fundamental = conn.execute(
            text("""
                SELECT final_grade, allowed_trade_types
                FROM fundamental_grades_final
                WHERE symbol = :symbol
            """),
            {"symbol": symbol}
        ).fetchone()

        if not fundamental:
            return None

        grade, allowed = fundamental

        if grade not in ("STRONG", "AVERAGE"):
            return None

        if "weekly" not in allowed:
            return None

        # -------------------------------
        # 6️⃣ MARKET REGIME GATE
        # -------------------------------
        regime = conn.execute(
            text("""
                SELECT market_regime
                FROM market_regime
                WHERE trade_date = :trade_date
            """),
            {"trade_date": trade_date}
        ).scalar()

        if regime not in ("TREND", "RANGE"):
            return None

        # -------------------------------
        # 7️⃣ NEWS FILTER (LAST 3 DAYS)
        # -------------------------------
        negative_news = conn.execute(
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

        if negative_news and negative_news > 0:
            return None

        # -------------------------------
        # ✅ BREAKOUT CONFIRMED
        # -------------------------------
        return {
            "symbol": symbol,
            "strategy": "WEEKLY_BREAKOUT",
            "entry_above": float(range_high),
            "stop_loss": float(range_low),
            "confidence": "HIGH" if regime == "TREND" else "MEDIUM"
        }


