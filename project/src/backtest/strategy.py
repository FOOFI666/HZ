from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ..config import EXECUTION_CONFIG, STRATEGY_CONFIG
from .execution import apply_position_management, compute_range_levels, generate_entries


def calc_expansion_score(row: pd.Series) -> float:
    score = 0.0
    if row.get("is_compressed_regime"):
        score += 1.0
    if row.get("net_oi_z", 0.0) > STRATEGY_CONFIG.expansion_net_oi_z_thr:
        score += 1.0
    if abs(row.get("funding_dev", 0.0)) < STRATEGY_CONFIG.expansion_funding_dev_thr:
        score += 1.0
    return score


def calc_risk_score(row: pd.Series) -> float:
    score = 0.0
    if abs(row.get("funding_bps", 0.0)) > STRATEGY_CONFIG.risk_funding_abs_thr:
        score += 1.0
    if abs(row.get("basis_bps", 0.0)) > STRATEGY_CONFIG.risk_basis_thr:
        score += 1.0
    if row.get("dom_perp", 0.0) > STRATEGY_CONFIG.risk_dom_thr and row.get("net_oi_z", 0.0) > 0:
        score += 1.0
    return score


def trade_allowed(row: pd.Series) -> bool:
    expansion = calc_expansion_score(row)
    risk = calc_risk_score(row)
    return expansion >= 2.0 and risk < 2.0


@dataclass
class BreakoutStrategy:
    name: str = "breakout_v1"

    def run(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        df = df.copy()
        df = compute_range_levels(df)
        df = generate_entries(df, trade_allowed)
        trades, equity = apply_position_management(df, EXECUTION_CONFIG)
        return trades, equity
