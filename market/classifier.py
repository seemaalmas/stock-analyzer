def classify_regime(nifty_trend, bank_trend, breadth_ratio, vix):
    if vix is None:
        return "NO_DATA"

    # High volatility overrides everything
    if vix > 20:
        if nifty_trend == "DOWN":
            return "NO_TRADE"
        return "VOLATILE"

    # Strong trending market
    if (
        nifty_trend == "UP"
        and bank_trend == "UP"
        and breadth_ratio > 0.6
    ):
        return "TREND"

    # Range-bound market
    if 0.4 <= breadth_ratio <= 0.6:
        return "RANGE"

    return "CAUTION"
