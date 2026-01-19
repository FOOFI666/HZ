from __future__ import annotations

import numpy as np
import pandas as pd


def compute_metrics(trades: pd.DataFrame, equity_curve: pd.DataFrame) -> dict[str, float]:
    metrics: dict[str, float] = {}
    if equity_curve.empty:
        return metrics
    equity = equity_curve["equity"].values
    returns = np.diff(equity, prepend=equity[0]) / equity
    metrics["total_return"] = equity[-1] - 1.0
    drawdown = equity / np.maximum.accumulate(equity) - 1.0
    metrics["max_drawdown"] = drawdown.min()
    if trades.empty:
        metrics.update(
            {
                "winrate": 0.0,
                "profit_factor": 0.0,
                "avg_r_multiple": 0.0,
                "expectancy": 0.0,
                "trades": 0.0,
                "avg_trade_duration": 0.0,
            }
        )
        return metrics
    wins = trades[trades["pnl"] > 0]
    losses = trades[trades["pnl"] <= 0]
    metrics["winrate"] = len(wins) / len(trades)
    metrics["profit_factor"] = wins["pnl"].sum() / abs(losses["pnl"].sum() or 1e-9)
    metrics["avg_r_multiple"] = trades["pnl"].mean()
    metrics["expectancy"] = trades["pnl"].mean() * metrics["winrate"]
    metrics["trades"] = float(len(trades))
    metrics["avg_trade_duration"] = (trades["exit_time"] - trades["entry_time"]).mean()
    if returns.std() > 0:
        metrics["sharpe"] = returns.mean() / returns.std() * np.sqrt(365 * 24 * 60)
    return metrics


def compute_event_metrics(df_with_labels: pd.DataFrame, trades: pd.DataFrame) -> dict[str, float]:
    if trades.empty or "y_pump25" not in df_with_labels.columns:
        return {"recall_pump25": 0.0, "false_positive_rate": 0.0}
    pump_events = df_with_labels[df_with_labels["y_pump25"]]
    traded_times = set(trades["entry_time"].astype(int))
    recall = pump_events["t"].isin(traded_times).mean() if not pump_events.empty else 0.0
    false_positives = trades[~trades["entry_time"].astype(int).isin(pump_events["t"].astype(int))]
    false_positive_rate = len(false_positives) / len(trades)
    return {"recall_pump25": float(recall), "false_positive_rate": float(false_positive_rate)}
