from __future__ import annotations

REQUIRED_OHLCV = ["date", "open", "high", "low", "close", "volume"]


def require_columns(df, required: list[str]) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
