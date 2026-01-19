from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from .config import DATA_CONFIG
from .features_A import add_spot_perp_features
from .features_B import add_funding_features
from .features_C import add_structural_liquidity
from .features_F import add_oi_features
from .funding import align_funding_to_minutes, download_funding
from .klines import download_perp_1m, download_spot_1m
from .oi import align_oi_to_minutes, download_oi_hist


def save_parquet(df: pd.DataFrame, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def build_features_for_symbol(symbol: str, start_ms: int, end_ms: int) -> pd.DataFrame:
    spot = download_spot_1m(symbol, start_ms, end_ms)
    perp = download_perp_1m(symbol, start_ms, end_ms)

    if spot.empty or perp.empty:
        return pd.DataFrame()

    spot = spot.rename(columns={"close": "spot_close", "quote_vol": "spot_quote_vol"})
    perp = perp.rename(
        columns={
            "close": "perp_close",
            "high": "perp_high",
            "low": "perp_low",
            "quote_vol": "perp_quote_vol",
        }
    )

    df = pd.merge(
        spot[["t", "spot_close", "spot_quote_vol"]],
        perp[["t", "perp_close", "perp_high", "perp_low", "perp_quote_vol"]],
        on="t",
        how="inner",
    )

    funding_raw = download_funding(symbol, start_ms, end_ms)
    funding = align_funding_to_minutes(funding_raw, start_ms, end_ms)
    oi_raw = download_oi_hist(symbol, DATA_CONFIG.oi_period, start_ms, end_ms)
    oi = align_oi_to_minutes(oi_raw, start_ms, end_ms)

    df = df.merge(funding, on="t", how="left").merge(oi, on="t", how="left")
    df["funding_rate"] = df["funding_rate"].fillna(0.0)
    df["oi"] = df["oi"].fillna(0.0)

    df = add_spot_perp_features(df)
    df = add_funding_features(df)
    df = add_oi_features(df)
    df = add_structural_liquidity(df)
    return df


def persist_raw_data(symbol: str, spot: pd.DataFrame, perp: pd.DataFrame, funding: pd.DataFrame, oi: pd.DataFrame, base_dir: str) -> None:
    spot_path = os.path.join(base_dir, "raw", "spot_1m", f"{symbol}.parquet")
    perp_path = os.path.join(base_dir, "raw", "perp_1m", f"{symbol}.parquet")
    funding_path = os.path.join(base_dir, "raw", "funding", f"{symbol}.parquet")
    oi_path = os.path.join(base_dir, "raw", "oi", f"{symbol}.parquet")

    save_parquet(spot, spot_path)
    save_parquet(perp, perp_path)
    save_parquet(funding, funding_path)
    save_parquet(oi, oi_path)
