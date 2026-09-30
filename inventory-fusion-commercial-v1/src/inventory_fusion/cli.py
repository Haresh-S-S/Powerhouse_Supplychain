from __future__ import annotations

import argparse
from pathlib import Path

from inventory_fusion.backtest import (
    make_fused_forecasts,
    rolling_backtest,
    temporal_tune_test_split,
)
from inventory_fusion.data import load_inventory_csv, synthetic_inventory_series
from inventory_fusion.forecasters import (
    CalendarRidgeForecaster,
    Chronos2Forecaster,
    CrostonForecaster,
    LinearTrendForecaster,
    MovingAverageForecaster,
    SeasonalNaiveForecaster,
    TimesFMForecaster,
    TTMForecaster,
)
from inventory_fusion.fusion import AdaptiveFusion
from inventory_fusion.registry import ModelRegistry
from inventory_fusion.report import write_report


def default_forecasters():
    return [
        SeasonalNaiveForecaster(7),
        MovingAverageForecaster(28),
        LinearTrendForecaster(),
        CrostonForecaster(),
        CalendarRidgeForecaster(),
    ]


def _run(series, output: Path, horizon: int, min_train: int, step: int, forecasters=None) -> None:
    forecasters = forecasters or default_forecasters()
    try:
        records = rolling_backtest(
            series,
            forecasters,
            horizon=horizon,
            min_train=min_train,
            step=step,
        )
        tune, test = temporal_tune_test_split(records)
        fusion = AdaptiveFusion().fit(tune)
        fused = make_fused_forecasts(test, fusion)
        artifacts = write_report(output, test, fusion, fused)
        print(f"Backtest complete: {len(tune)} tuning windows, {len(test)} holdout windows")
        for name, path in artifacts.items():
            print(f"{name}: {path.resolve()}")
    finally:
        for forecaster in forecasters:
            forecaster.close()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="inventory-fusion")
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo = subparsers.add_parser("demo", help="run an end-to-end synthetic proof")
    demo.add_argument("--output", type=Path, default=Path("outputs/demo"))
    demo.add_argument("--skus", type=int, default=18)
    demo.add_argument("--days", type=int, default=420)
    demo.add_argument("--horizon", type=int, default=14)

    backtest = subparsers.add_parser("backtest", help="run a CSV rolling backtest")
    backtest.add_argument("--data", type=Path, required=True)
    backtest.add_argument("--output", type=Path, default=Path("outputs/backtest"))
    backtest.add_argument("--horizon", type=int, default=14)
    backtest.add_argument("--min-train", type=int, default=180)
    backtest.add_argument("--step", type=int, default=14)

    hf_smoke = subparsers.add_parser(
        "hf-smoke", help="run locked TTM, Chronos-2 and TimesFM together on GPU"
    )
    hf_smoke.add_argument("--output", type=Path, default=Path("outputs/hf-smoke"))
    hf_smoke.add_argument("--skus", type=int, default=3)
    hf_smoke.add_argument("--days", type=int, default=336)
    hf_smoke.add_argument("--horizon", type=int, default=14)

    args = parser.parse_args(argv)
    if args.command == "demo":
        series = synthetic_inventory_series(n_skus=args.skus, n_days=args.days)
        _run(series, args.output, args.horizon, min_train=180, step=args.horizon)
    elif args.command == "backtest":
        _run(
            load_inventory_csv(args.data),
            args.output,
            args.horizon,
            args.min_train,
            args.step,
        )
    elif args.command == "hf-smoke":
        ModelRegistry.load().require_commercial(
            ["ttm_r2_1_daily", "chronos_2", "timesfm_2_5"]
        )
        series = synthetic_inventory_series(n_skus=args.skus, n_days=args.days)
        forecasters = [
            SeasonalNaiveForecaster(7),
            CalendarRidgeForecaster(),
            TTMForecaster(),
            Chronos2Forecaster(),
            TimesFMForecaster(),
        ]
        _run(
            series,
            args.output,
            args.horizon,
            min_train=max(180, args.days // 2),
            step=args.horizon,
            forecasters=forecasters,
        )


if __name__ == "__main__":
    main()
