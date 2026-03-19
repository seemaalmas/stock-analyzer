from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class RegimePoint:
    date: datetime
    regime: str
    metrics: dict[str, Any]


@dataclass(frozen=True)
class StructurePoint:
    date: datetime
    swing_high: bool
    swing_low: bool
    trend_state: str  # "HH","HL","LH","LL","UNKNOWN"
    metrics: dict[str, Any]


@dataclass(frozen=True)
class ScoreResult:
    date: datetime
    score: int  # 0..100
    bucket: str  # "LOW","MEDIUM","HIGH"
    reasons: list[str]
    metadata: dict[str, Any]
