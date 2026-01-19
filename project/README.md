# Binance Market Phase Research Toolkit

Проект собирает спот и USD-M perpetual данные Binance за последние N дней, строит minute-level features, и запускает MVP-бэктест стратегии breakout.

## Структура

```
project/
  src/
    config.py
    binance_http.py
    symbols.py
    klines.py
    funding.py
    oi.py
    features_A.py
    features_B.py
    features_F.py
    features_C.py
    feature_merge.py
    labels.py
    backtest/
      engine.py
      strategy.py
      execution.py
      metrics.py
      reports.py
  data/
    raw/
      spot_1m/
      perp_1m/
      funding/
      oi/
    features/
      per_symbol/
    backtests/
      runs/
  run_build_dataset.py
  run_backtest.py
  README.md
```

## Быстрый старт

```bash
python run_build_dataset.py --days 30 --symbols BTCUSDT,ETHUSDT
python run_backtest.py --days 30 --symbols BTCUSDT,ETHUSDT --strategy breakout_v1
```

## Основные функции API

- `get_spot_symbols()`
- `get_perp_symbols()`
- `download_spot_1m()` / `download_perp_1m()`
- `download_funding()` / `download_oi_hist()`
- `build_features_for_symbol()`
- `make_labels()`

## Хранилище

Данные сохраняются в `data/raw` и `data/features/per_symbol`, результаты бэктеста — в `data/backtests/runs/{run_id}`.
