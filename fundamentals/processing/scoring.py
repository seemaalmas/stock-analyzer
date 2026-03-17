def score_fundamentals(metrics):
    score = 0

    if metrics["roce"] > 0.20:
        score += 15
    elif metrics["roce"] > 0.15:
        score += 10
    elif metrics["roce"] > 0.10:
        score += 5

    if metrics["net_margin"] > 0.10:
        score += 10
    elif metrics["net_margin"] > 0.05:
        score += 5

    if metrics["revenue_yoy"] > 0.12:
        score += 10

    if metrics["profit_yoy"] > 0.12:
        score += 10

    if metrics["debt_equity"] < 0.5:
        score += 20
    elif metrics["debt_equity"] < 1:
        score += 10

    return score
