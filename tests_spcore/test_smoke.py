"""Smoke test – verifies core imports work and scoring produces valid output.

No external services (DB, network) required. Safe for CI.
"""

import pandas as pd

from spcore.models import ScoreResult
from spcore.scoring import score_ohlcv


def test_import_and_score():
    """Import scoring module, feed minimal OHLCV data, and validate output."""
    df = pd.DataFrame(
        {
            "date": ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2025-01-05"],
            "open": [100, 105, 110, 108, 112],
            "high": [110, 115, 118, 115, 120],
            "low": [95, 100, 105, 103, 108],
            "close": [105, 112, 115, 110, 118],
            "volume": [1000, 1500, 1200, 1800, 3000],
        }
    )
    result = score_ohlcv(df)

    assert isinstance(result, ScoreResult)
    assert 0 <= result.score <= 100
    assert result.bucket in ("LOW", "MEDIUM", "HIGH")
    assert isinstance(result.reasons, list)
    assert len(result.reasons) > 0
    assert result.date is not None
