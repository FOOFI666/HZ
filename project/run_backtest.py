from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd

from src.backtest.engine import BacktestEngine
from src.backtest.strategy import BreakoutStrategy
from src.config import EXECUTION_CONFIG
from src.labels import make_labels
from src.symbols import get_symbol_intersection


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--symbols", type=str, default="all")
    parser.add_argument("--strategy", type=str, default="breakout_v1")
    parser.add_argument("--leverage", type=float, default=EXECUTION_CONFIG.leverage)
    parser.add_argument("--fee_bps", type=float, default=EXECUTION_CONFIG.fee_bps)
    parser.add_argument("--slippage_bps", type=float, default=EXECUTION_CONFIG.slippage_bps)
    parser.add_argument("--features_dir", type=str, default="data/features/per_symbol")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - args.days * 24 * 60 * 60 * 1000

    if args.symbols == "all":
        symbols = get_symbol_intersection()
    else:
        symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]

    strategy = BreakoutStrategy()
    engine = BacktestEngine(params={"strategy": args.strategy, "leverage": args.leverage, "fee_bps": args.fee_bps})

    for symbol in symbols:
        path = Path(args.features_dir) / f"{symbol}.parquet"
        if not path.exists():
            continue
        df = pd.read_parquet(path)
        df = df[(df["t"] >= start_ms) & (df["t"] <= end_ms)]
        labels = make_labels(df)
        result = engine.run(strategy, df, labels)
        print(f"{symbol} run {result.run_id} metrics: {result.metrics}")


if __name__ == "__main__":
    main()
