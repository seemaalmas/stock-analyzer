def detect_red_flags(metrics, promoter_trend, pledge_pct):
    flags = []

    if pledge_pct > 25:
        flags.append("HIGH_PLEDGE")

    if promoter_trend == "DECREASING":
        flags.append("PROMOTER_SELLING")

    if metrics["debt_equity"] > 2:
        flags.append("HIGH_DEBT")

    if metrics["profit_yoy"] < 0 and metrics["revenue_yoy"] < 0:
        flags.append("DECLINING_BUSINESS")

    return flags
