def map_score_to_probability(score):
    if score < 40:
        return 20, "Very Low"
    elif score < 55:
        return 35, "Low"
    elif score < 70:
        return 50, "Medium"
    elif score < 85:
        return 65, "High"
    else:
        return 75, "Very High"
