from __future__ import annotations

from datetime import datetime

import pandas as pd

from spcore.models import ScoreResult
from spcore.validation import require_columns, REQUIRED_OHLCV


def score_ohlcv(df: pd.DataFrame) -> ScoreResult:
    """Score an OHLCV DataFrame and return a ScoreResult.

    Expects columns: date, open, high, low, close, volume.
    Uses the last row's date as the result date.
    """
    require_columns(df, REQUIRED_OHLCV)
    if df.empty:
        raise ValueError("DataFrame is empty")

    df = df.sort_values("date").reset_index(drop=True)
    last = df.iloc[-1]

    reasons: list[str] = []
    score = 50  # baseline

    # --- simple momentum: close vs open of last bar ---
    if last["close"] > last["open"]:
        score += 10
        reasons.append("Last bar closed green")
    elif last["close"] < last["open"]:
        score -= 10
        reasons.append("Last bar closed red")

    # --- volume spike check (last bar vs mean) ---
    if len(df) >= 2:
        avg_vol = df["volume"].iloc[:-1].mean()
        if avg_vol > 0 and last["volume"] > 1.5 * avg_vol:
            score += 10
            reasons.append("Volume spike detected")

    # --- price range breadth ---
    if len(df) >= 5:
        recent = df.tail(5)
        high_range = recent["high"].max() - recent["low"].min()
        mid = (recent["high"].max() + recent["low"].min()) / 2
        if mid > 0 and high_range / mid > 0.05:
            score += 5
            reasons.append("Wide range in last 5 bars")

    score = max(0, min(100, score))

    if score >= 70:
        bucket = "HIGH"
    elif score >= 40:
        bucket = "MEDIUM"
    else:
        bucket = "LOW"

    if not reasons:
        reasons.append("No notable signals")

    result_date = pd.Timestamp(last["date"]).to_pydatetime()
    if not isinstance(result_date, datetime):
        result_date = datetime.now()

    return ScoreResult(
        date=result_date,
        score=score,
        bucket=bucket,
        reasons=reasons,
        metadata={"rows": len(df)},
    )
