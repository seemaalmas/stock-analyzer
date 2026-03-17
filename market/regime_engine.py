def classify_market_regime(
    nifty_trend,
    bank_trend,
    ad_ratio,
    vix,
    gap_pct
):
    # HARD BLOCKS
    if vix is None or ad_ratio is None:
        return "NO_TRADE"

    if vix > 18:
        return "NO_TRADE"

    if abs(gap_pct) > 1.5:
        return "NO_TRADE"

    if ad_ratio < 0.6:
        return "NO_TRADE"

    # TREND DAY
    if (
        nifty_trend == "UP"
        and bank_trend == "UP"
        and ad_ratio >= 1.5
        and vix < 15
    ):
        return "TREND_DAY"

    # TRAP DAY
    if nifty_trend == "UP" and ad_ratio < 0.8:
        return "TRAP_DAY"

    # RANGE DAY
    return "RANGE_DAY"
