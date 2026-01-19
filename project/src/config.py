from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DataConfig:
    lookback_days: int = 30
    interval: str = "1m"
    klines_limit: int = 1000
    oi_period: str = "5m"
    rate_limit_per_sec: int = 8
    max_retries: int = 5
    retry_backoff_sec: float = 1.5


@dataclass(frozen=True)
class FeatureConfig:
    funding_mean_window: int = 1440
    net_oi_z_window: int = 720
    range_window: int = 240
    range_compress_window: int = 240
    range_compress_pct: float = 0.015
    breakout_lookback: int = 240


@dataclass(frozen=True)
class StrategyConfig:
    expansion_net_oi_z_thr: float = 1.5
    expansion_funding_dev_thr: float = 5.0
    risk_funding_abs_thr: float = 15.0
    risk_basis_thr: float = 30.0
    risk_dom_thr: float = 0.6


@dataclass(frozen=True)
class ExecutionConfig:
    leverage: float = 5.0
    fee_bps: float = 4.0
    slippage_bps: float = 2.0
    stop_buffer_pct: float = 0.0
    trailing_window: int = 60
    rr_target: float = 2.0


DATA_CONFIG = DataConfig()
FEATURE_CONFIG = FeatureConfig()
STRATEGY_CONFIG = StrategyConfig()
EXECUTION_CONFIG = ExecutionConfig()
