from __future__ import annotations

import pandas as pd

from .config import FEATURE_CONFIG


def add_structural_liquidity(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    window = FEATURE_CONFIG.range_window
    df["range_high"] = df["perp_close"].rolling(window).max()
    df["range_low"] = df["perp_close"].rolling(window).min()
    df["dist_to_last_high_pct"] = (df["range_high"] - df["perp_close"]) / df["perp_close"]
    df["dist_to_last_low_pct"] = (df["perp_close"] - df["range_low"]) / df["perp_close"]
    df["range_width_pct"] = (df["range_high"] - df["range_low"]) / df["perp_close"]

    compress_window = FEATURE_CONFIG.range_compress_window
    df["range_duration"] = compress_window
    df["is_range_compressed"] = df["range_width_pct"] < FEATURE_CONFIG.range_compress_pct
    df["breakout_potential"] = (
        df["range_width_pct"].rolling(compress_window).mean().fillna(0.0)
    )
    df["is_compressed_regime"] = df["is_range_compressed"].rolling(compress_window).max().fillna(0.0).astype(bool)
    return df
