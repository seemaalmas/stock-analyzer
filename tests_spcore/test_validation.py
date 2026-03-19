import pandas as pd
import pytest
from spcore.validation import require_columns


def test_require_columns_missing():
    df = pd.DataFrame({"date": [1], "close": [1]})
    with pytest.raises(ValueError) as e:
        require_columns(df, ["date", "open"])
    assert "Missing required columns" in str(e.value)
