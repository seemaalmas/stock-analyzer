from sqlalchemy import text
from database.engine import engine
from datetime import timedelta

def build_context(signal, trade_date):
    symbol = signal["symbol"]

    with engine.connect() as conn:

        # Market regime
        regime = conn.execute(
            text("""
                SELECT market_regime
                FROM market_regime
                WHERE trade_date = :date
            """),
            {"date": trade_date}
        ).scalar()

        # Structure
        structure = conn.execute(
            text("""
                SELECT structure_type, duration
                FROM price_structure
                WHERE symbol = :symbol
                  AND detected_on = :date
            """),
            {"symbol": symbol, "date": trade_date}
        ).fetchone()

        structure_label = "WEAK"
        if structure:
            stype, duration = structure
            if stype == "HH_HL" and duration >= 30:
                structure_label = "HH_HL_LONG"
            elif stype == "RANGE" and duration >= 20:
                structure_label = "RANGE_STRONG"

        # Indicators
        ind = conn.execute(
            text("""
                SELECT ema20, ema50, ema200, rsi, vwap_state
                FROM technical_state
                WHERE symbol = :symbol
                  AND as_of_date = :date
            """),
            {"symbol": symbol, "date": trade_date}
        ).fetchone()

        ema_alignment = False
        rsi_healthy = False
        vwap_ok = False

        if ind:
            ema20, ema50, ema200, rsi, vwap_state = ind
            ema_alignment = ema20 > ema50 > ema200
            rsi_healthy = 45 <= rsi <= 70
            vwap_ok = vwap_state != "BELOW_VWAP"

        # Fundamentals
        fund = conn.execute(
            text("""
                SELECT final_grade
                FROM fundamental_grades_final
                WHERE symbol = :symbol
            """),
            {"symbol": symbol}
        ).scalar()

        # News sentiment
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

        news_sentiment = "NEGATIVE" if neg_news and neg_news > 0 else "NEUTRAL"

    return {
        "market_regime": regime,
        "structure": structure_label,
        "ema_alignment": ema_alignment,
        "rsi_healthy": rsi_healthy,
        "vwap_ok": vwap_ok,
        "fundamental_grade": fund,
        "news_sentiment": news_sentiment
    }
