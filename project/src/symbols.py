from __future__ import annotations

from typing import Iterable

from .binance_http import FUTURES_HTTP, SPOT_HTTP


def get_spot_symbols() -> list[str]:
    data = SPOT_HTTP.get("/api/v3/exchangeInfo", {})
    symbols = []
    for info in data.get("symbols", []):
        if info.get("quoteAsset") == "USDT" and info.get("status") == "TRADING":
            symbols.append(info["symbol"])
    return sorted(symbols)


def get_perp_symbols() -> list[str]:
    data = FUTURES_HTTP.get("/fapi/v1/exchangeInfo", {})
    symbols = []
    for info in data.get("symbols", []):
        if (
            info.get("quoteAsset") == "USDT"
            and info.get("contractType") == "PERPETUAL"
            and info.get("status") == "TRADING"
        ):
            symbols.append(info["symbol"])
    return sorted(symbols)


def get_symbol_intersection(preferred: Iterable[str] | None = None) -> list[str]:
    spot = set(get_spot_symbols())
    perp = set(get_perp_symbols())
    symbols = sorted(spot & perp)
    if preferred:
        preferred_set = set(preferred)
        symbols = [s for s in symbols if s in preferred_set]
    return symbols
