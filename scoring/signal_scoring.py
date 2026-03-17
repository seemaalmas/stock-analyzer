def score_signal(signal, context):
    score = 20  # BASE SCORE (IMPORTANT)

    regime = context["market_regime"]
    if regime == "TREND":
        score += 20
    elif regime == "RANGE":
        score += 10
    elif regime == "VOLATILE":
        score -= 10
    else:
        score += 0  # NOT return None

    if signal["strategy"] == "WEEKLY_PULLBACK":
        score += 15
    else:
        score += 10

    structure = context["structure"]
    if structure == "HH_HL_LONG":
        score += 15
    elif structure == "RANGE_STRONG":
        score += 12
    else:
        score += 5

    if context["ema_alignment"]:
        score += 10
    if context["rsi_healthy"]:
        score += 5
    if context["vwap_ok"]:
        score += 5

    grade = context["fundamental_grade"]
    if grade == "STRONG":
        score += 15
    elif grade == "AVERAGE":
        score += 8
    else:
        score -= 5   # NOT -20 yet

    news = context["news_sentiment"]
    if news == "NEGATIVE":
        score -= 10
    else:
        score += 5

    return max(score, 0)
