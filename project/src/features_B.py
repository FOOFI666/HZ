from __future__ import annotations

import pandas as pd

from .config import FEATURE_CONFIG


def add_funding_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["funding_bps"] = df["funding_rate"] * 10_000
    df["funding_mean_1d"] = df["funding_bps"].rolling(FEATURE_CONFIG.funding_mean_window).mean()
    df["funding_dev"] = df["funding_bps"] - df["funding_mean_1d"]
    return df
