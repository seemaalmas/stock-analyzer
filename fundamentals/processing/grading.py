def grade_stock(score, red_flags):
    if red_flags:
        return "AVOID", []

    if score >= 75:
        return "STRONG", ["weekly", "monthly"]
    elif score >= 60:
        return "GOOD", ["weekly"]
    elif score >= 45:
        return "AVERAGE", ["intraday"]
    else:
        return "WEAK", []
