from __future__ import annotations

import json
import uuid
from pathlib import Path

import pandas as pd


def save_run(trades: pd.DataFrame, equity: pd.DataFrame, metrics: dict, params: dict) -> str:
    run_id = uuid.uuid4().hex[:10]
    base = Path("data/backtests/runs") / run_id
    base.mkdir(parents=True, exist_ok=True)

    trades.to_parquet(base / "trades.parquet", index=False)
    equity.to_parquet(base / "equity.parquet", index=False)
    (base / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (base / "params.json").write_text(json.dumps(params, indent=2), encoding="utf-8")

    summary = [f"run_id: {run_id}"]
    for key, value in metrics.items():
        summary.append(f"{key}: {value}")
    (base / "summary.txt").write_text("\n".join(summary), encoding="utf-8")
    return run_id
