"""Signal scoring routes."""

from __future__ import annotations

from datetime import datetime
from typing import List

import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel

from spcore.scoring import score_ohlcv

router = APIRouter(prefix="/signals", tags=["signals"])


class OHLCVBar(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class ScoreRequest(BaseModel):
    bars: List[OHLCVBar]


class ScoreResponse(BaseModel):
    date: str
    score: int
    bucket: str
    reasons: List[str]


@router.post("/score", response_model=ScoreResponse)
def post_score(req: ScoreRequest):
    records = [b.model_dump() for b in req.bars]
    df = pd.DataFrame(records)
    result = score_ohlcv(df)
    return ScoreResponse(
        date=result.date.isoformat() if isinstance(result.date, datetime) else str(result.date),
        score=result.score,
        bucket=result.bucket,
        reasons=result.reasons,
    )
