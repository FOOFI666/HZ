from __future__ import annotations

import pandas as pd

from .binance_http import FUTURES_HTTP


def download_oi_hist(
    symbol: str,
    period: str,
    start_ms: int,
    end_ms: int,
) -> pd.DataFrame:
    rows = []
    start = start_ms
    while start < end_ms:
        data = FUTURES_HTTP.get(
            "/futures/data/openInterestHist",
            {
                "symbol": symbol,
                "period": period,
                "startTime": start,
                "endTime": end_ms,
                "limit": 500,
            },
        )
        if not data:
            break
        rows.extend(data)
        last = int(data[-1]["timestamp"])
        if last == start:
            break
        start = last + 1
        if len(data) < 500:
            break
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.rename(columns={"timestamp": "t", "sumOpenInterest": "oi"})
    df = df[["t", "oi"]]
    df = df.astype({"t": "int64", "oi": "float64"})
    return df


def align_oi_to_minutes(df: pd.DataFrame, start_ms: int, end_ms: int) -> pd.DataFrame:
    if df.empty:
        idx = pd.date_range(
            pd.to_datetime(start_ms, unit="ms"),
            pd.to_datetime(end_ms, unit="ms"),
            freq="1min",
            inclusive="left",
        )
        return pd.DataFrame({"t": (idx.view("int64") // 1_000_000).astype("int64"), "oi": 0.0})
    df = df.copy()
    df["t"] = pd.to_datetime(df["t"], unit="ms")
    df = df.set_index("t").sort_index()
    idx = pd.date_range(
        pd.to_datetime(start_ms, unit="ms"),
        pd.to_datetime(end_ms, unit="ms"),
        freq="1min",
        inclusive="left",
    )
    df = df.reindex(idx).ffill().fillna(0.0)
    df["t"] = (df.index.view("int64") // 1_000_000).astype("int64")
    df = df.reset_index(drop=True)
    return df[["t", "oi"]]
