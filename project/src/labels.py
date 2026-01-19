from __future__ import annotations

import pandas as pd


def make_labels(
    df: pd.DataFrame,
    horizons: list[int] | None = None,
    thresholds: list[float] | None = None,
) -> pd.DataFrame:
    horizons = horizons or [60, 120, 240]
    thresholds = thresholds or [0.03, 0.07, 0.25]
    out = df.copy()

    for horizon in horizons:
        price_high = out.get("perp_high", out["perp_close"])
        price_low = out.get("perp_low", out["perp_close"])
        max_up = (
            price_high.rolling(horizon, min_periods=1).max().shift(-horizon)
            / out["perp_close"]
            - 1.0
        )
        max_down = (
            price_low.rolling(horizon, min_periods=1).min().shift(-horizon)
            / out["perp_close"]
            - 1.0
        )
        out[f"max_up_move_next_{horizon}"] = max_up
        out[f"max_down_move_next_{horizon}"] = max_down

        y_expansion = pd.Series(0, index=out.index)
        y_expansion = y_expansion.where(max_up < thresholds[0], 1)
        y_expansion = y_expansion.where(max_up < thresholds[1], 2)
        out[f"y_expansion_{horizon}"] = y_expansion

    out["y_pump25"] = out[f"max_up_move_next_{horizons[0]}"] >= thresholds[2]
    return out
