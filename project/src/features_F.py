from __future__ import annotations

import pandas as pd

from .config import FEATURE_CONFIG


def add_oi_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["oi_value"] = df["oi"] * df["perp_close"]
    df["net_oi"] = df["oi"].diff()
    df["net_oi_pct"] = df["net_oi"] / df["oi"].replace(0, pd.NA)
    rolling = df["net_oi"].rolling(FEATURE_CONFIG.net_oi_z_window)
    df["net_oi_z"] = (df["net_oi"] - rolling.mean()) / rolling.std()
    df["net_oi_z"] = df["net_oi_z"].fillna(0.0)
    return df
