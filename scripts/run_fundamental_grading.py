from fundamentals.repository import (
    fetch_annual_financials,
    save_fundamental_grade
)
from fundamentals.processing.normalization import normalize_financials
from fundamentals.processing.red_flags import detect_red_flags
from fundamentals.processing.scoring import score_fundamentals
from fundamentals.processing.grading import grade_stock

def run(symbol):
    df = fetch_annual_financials(symbol)

    if len(df) < 2:
        print(f"❌ Skipping {symbol}: insufficient data")
        return

    metrics = normalize_financials(df)
    flags = detect_red_flags(
        metrics,
        promoter_trend="STABLE",
        pledge_pct=5
    )
    score = score_fundamentals(metrics)
    grade, trade_types = grade_stock(score, flags)

    save_fundamental_grade(
        symbol,
        score,
        grade,
        flags,
        trade_types
    )

    print(f"✅ {symbol} → Grade: {grade}, Score: {score}")

if __name__ == "__main__":
    run("TCS")
