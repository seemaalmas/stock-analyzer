def normalize_financials(df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    metrics = {}

    metrics["roce"] = (
        latest["operating_profit"] /
        (latest["equity"] + latest["debt"])
    )

    metrics["net_margin"] = (
        latest["net_profit"] / latest["revenue"]
    )

    metrics["revenue_yoy"] = (
        (latest["revenue"] - prev["revenue"]) / prev["revenue"]
    )

    metrics["profit_yoy"] = (
        (latest["net_profit"] - prev["net_profit"]) /
        abs(prev["net_profit"])
    )

    metrics["debt_equity"] = (
        latest["debt"] / latest["equity"]
    )

    return metrics
