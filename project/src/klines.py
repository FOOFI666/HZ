from __future__ import annotations

from typing import Any

import pandas as pd

from .binance_http import FUTURES_HTTP, SPOT_HTTP
from .config import DATA_CONFIG


KLINE_COLUMNS = [
    "t",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_vol",
    "trades",
    "taker_base",
    "taker_quote",
    "ignore",
]


def _fetch_klines(
    http_client: Any,
    path: str,
    symbol: str,
    start_ms: int,
    end_ms: int,
) -> pd.DataFrame:
    rows: list[list[Any]] = []
    start = start_ms
    while start < end_ms:
        data = http_client.get(
            path,
            {
                "symbol": symbol,
                "interval": DATA_CONFIG.interval,
                "startTime": start,
                "endTime": end_ms,
                "limit": DATA_CONFIG.klines_limit,
            },
        )
        if not data:
            break
        rows.extend(data)
        last = data[-1][0]
        if last == start:
            break
        start = last + 60_000
        if len(data) < DATA_CONFIG.klines_limit:
            break
    df = pd.DataFrame(rows, columns=KLINE_COLUMNS)
    if df.empty:
        return df
    df = df[["t", "open", "high", "low", "close", "volume", "quote_vol"]]
    df = df.astype(
        {
            "t": "int64",
            "open": "float64",
            "high": "float64",
            "low": "float64",
            "close": "float64",
            "volume": "float64",
            "quote_vol": "float64",
        }
    )
    return df


def download_spot_1m(symbol: str, start_ms: int, end_ms: int) -> pd.DataFrame:
    return _fetch_klines(SPOT_HTTP, "/api/v3/klines", symbol, start_ms, end_ms)


def download_perp_1m(symbol: str, start_ms: int, end_ms: int) -> pd.DataFrame:
    return _fetch_klines(FUTURES_HTTP, "/fapi/v1/klines", symbol, start_ms, end_ms)
