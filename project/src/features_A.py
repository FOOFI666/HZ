from __future__ import annotations

import pandas as pd


def add_spot_perp_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["basis_bps"] = (df["perp_close"] - df["spot_close"]) / df["spot_close"] * 10_000
    df["spread_abs"] = (df["perp_close"] - df["spot_close"]).abs()
    df["dom_perp"] = df["perp_quote_vol"] / (df["perp_quote_vol"] + df["spot_quote_vol"]).replace(0, 1)
    df["spot_dom"] = 1.0 - df["dom_perp"]
    return df
