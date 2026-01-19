from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests

from .config import DATA_CONFIG


@dataclass
class RateLimiter:
    rate_per_sec: int
    last_ts: float = 0.0

    def wait(self) -> None:
        now = time.time()
        min_interval = 1.0 / max(self.rate_per_sec, 1)
        if now - self.last_ts < min_interval:
            time.sleep(min_interval - (now - self.last_ts))
        self.last_ts = time.time()


class BinanceHTTP:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.session = requests.Session()
        self.limiter = RateLimiter(DATA_CONFIG.rate_limit_per_sec)

    def _reset_session(self) -> None:
        self.session.close()
        self.session = requests.Session()

    def get(self, path: str, params: dict[str, Any]) -> Any:
        url = f"{self.base_url}{path}"
        last_exception: Exception | None = None
        last_status: int | None = None
        last_body: str | None = None
        for attempt in range(DATA_CONFIG.max_retries):
            self.limiter.wait()
            try:
                response = self.session.get(url, params=params, timeout=15)
                last_status = response.status_code
                if response.status_code in {418, 429}:
                    last_body = response.text
                    time.sleep(DATA_CONFIG.retry_backoff_sec * (attempt + 1))
                    continue
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                last_exception = exc
                self._reset_session()
                time.sleep(DATA_CONFIG.retry_backoff_sec * (attempt + 1))
        details = []
        if last_status is not None:
            details.append(f"status={last_status}")
        if last_body:
            details.append(f"body={last_body[:200]}")
        if last_exception:
            details.append(f"error={last_exception}")
        suffix = f" ({', '.join(details)})" if details else ""
        raise RuntimeError(f"Failed request after retries: {url}{suffix}")


SPOT_HTTP = BinanceHTTP("https://api.binance.com")
FUTURES_HTTP = BinanceHTTP("https://fapi.binance.com")
