from __future__ import annotations

import argparse
import time
from pathlib import Path

from tqdm import tqdm

from src.config import DATA_CONFIG
from src.feature_merge import build_features_for_symbol, persist_raw_data, save_parquet
from src.funding import align_funding_to_minutes, download_funding
from src.klines import download_perp_1m, download_spot_1m
from src.oi import align_oi_to_minutes, download_oi_hist
from src.symbols import get_symbol_intersection


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=DATA_CONFIG.lookback_days)
    parser.add_argument("--tf", type=str, default=DATA_CONFIG.interval)
    parser.add_argument("--symbols", type=str, default="all")
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--out", type=str, default="data/features/per_symbol")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - args.days * 24 * 60 * 60 * 1000

    if args.symbols == "all":
        symbols = get_symbol_intersection()
    else:
        symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]

    base_dir = Path("data")
    base_dir.mkdir(exist_ok=True)

    for symbol in tqdm(symbols, desc="symbols"):
        try:
            spot = download_spot_1m(symbol, start_ms, end_ms)
            perp = download_perp_1m(symbol, start_ms, end_ms)
            funding_raw = download_funding(symbol, start_ms, end_ms)
            funding = align_funding_to_minutes(funding_raw, start_ms, end_ms)
            oi_raw = download_oi_hist(symbol, DATA_CONFIG.oi_period, start_ms, end_ms)
            oi = align_oi_to_minutes(oi_raw, start_ms, end_ms)
            persist_raw_data(symbol, spot, perp, funding, oi, str(base_dir))
            df = build_features_for_symbol(symbol, start_ms, end_ms)
            if df.empty:
                continue
            out_path = Path(args.out) / f"{symbol}.parquet"
            save_parquet(df, str(out_path))
        except Exception as exc:
            print(f"Failed symbol {symbol}: {exc}")


if __name__ == "__main__":
    main()
