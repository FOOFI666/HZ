from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ..config import FEATURE_CONFIG


@dataclass
class Position:
    side: str
    entry_price: float
    entry_time: int
    stop_price: float
    size: float


def compute_range_levels(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    window = FEATURE_CONFIG.range_window
    df["range_high"] = df["perp_close"].rolling(window).max()
    df["range_low"] = df["perp_close"].rolling(window).min()
    return df


def generate_entries(df: pd.DataFrame, trade_filter) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = False
    df["short_entry"] = False
    for idx in range(1, len(df)):
        row = df.iloc[idx]
        prev = df.iloc[idx - 1]
        if not trade_filter(row):
            continue
        if row["perp_close"] > prev["range_high"]:
            df.at[df.index[idx], "long_entry"] = True
        if row["perp_close"] < prev["range_low"]:
            df.at[df.index[idx], "short_entry"] = True
    return df


def apply_position_management(df: pd.DataFrame, params) -> tuple[pd.DataFrame, pd.DataFrame]:
    trades = []
    equity = []
    position: Position | None = None
    balance = 1.0

    for idx, row in df.iterrows():
        price = row["perp_close"]
        timestamp = row["t"]

        if position is None:
            if row.get("long_entry"):
                stop = row["range_low"] * (1 - params.stop_buffer_pct)
                position = Position("long", price, timestamp, stop, balance * params.leverage)
            elif row.get("short_entry"):
                stop = row["range_high"] * (1 + params.stop_buffer_pct)
                position = Position("short", price, timestamp, stop, balance * params.leverage)
        else:
            if position.side == "long":
                stop = max(position.stop_price, df.loc[:idx].tail(params.trailing_window)["perp_close"].min())
                position.stop_price = stop
                if price <= position.stop_price:
                    pnl = (price - position.entry_price) / position.entry_price
                    balance *= 1 + pnl * params.leverage - params.fee_bps / 10_000
                    trades.append(
                        {
                            "entry_time": position.entry_time,
                            "exit_time": timestamp,
                            "side": position.side,
                            "entry_price": position.entry_price,
                            "exit_price": price,
                            "pnl": pnl,
                            "balance": balance,
                        }
                    )
                    position = None
            else:
                stop = min(position.stop_price, df.loc[:idx].tail(params.trailing_window)["perp_close"].max())
                position.stop_price = stop
                if price >= position.stop_price:
                    pnl = (position.entry_price - price) / position.entry_price
                    balance *= 1 + pnl * params.leverage - params.fee_bps / 10_000
                    trades.append(
                        {
                            "entry_time": position.entry_time,
                            "exit_time": timestamp,
                            "side": position.side,
                            "entry_price": position.entry_price,
                            "exit_price": price,
                            "pnl": pnl,
                            "balance": balance,
                        }
                    )
                    position = None

        equity.append({"t": timestamp, "equity": balance})

    trades_df = pd.DataFrame(trades)
    equity_df = pd.DataFrame(equity)
    return trades_df, equity_df
