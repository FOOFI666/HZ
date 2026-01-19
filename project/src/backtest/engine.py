from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .metrics import compute_event_metrics, compute_metrics
from .reports import save_run


@dataclass
class BacktestResult:
    trades: pd.DataFrame
    equity_curve: pd.DataFrame
    metrics: dict[str, Any]
    params: dict[str, Any]
    run_id: str


class BacktestEngine:
    def __init__(self, params: dict[str, Any] | None = None) -> None:
        self.params = params or {}

    def run(self, strategy: Any, df: pd.DataFrame, labels: pd.DataFrame | None = None) -> BacktestResult:
        trades, equity = strategy.run(df)
        metrics = compute_metrics(trades, equity)
        if labels is not None:
            metrics.update(compute_event_metrics(labels, trades))
        run_id = save_run(trades, equity, metrics, self.params)
        return BacktestResult(trades=trades, equity_curve=equity, metrics=metrics, params=self.params, run_id=run_id)
