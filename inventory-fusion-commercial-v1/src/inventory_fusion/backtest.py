from __future__ import annotations

from collections.abc import Sequence

from inventory_fusion.forecasters.base import Forecaster
from inventory_fusion.fusion import AdaptiveFusion
from inventory_fusion.types import DEFAULT_QUANTILES, BacktestRecord, Forecast, TimeSeries


def rolling_backtest(
    series: Sequence[TimeSeries],
    forecasters: Sequence[Forecaster],
    *,
    horizon: int = 14,
    min_train: int = 180,
    step: int = 14,
    quantiles: tuple[float, ...] = DEFAULT_QUANTILES,
) -> list[BacktestRecord]:
    records: list[BacktestRecord] = []
    for item in series:
        if len(item.values) < min_train + horizon:
            continue
        segment = AdaptiveFusion.classify(
            item.values[:min_train],
            {name: values[:min_train] for name, values in item.covariates.items()},
        )
        for origin in range(min_train, len(item.values) - horizon + 1, step):
            history = item.slice(0, origin)
            future_dates = item.dates[origin : origin + horizon]
            future_covariates = {
                name: values[origin : origin + horizon] for name, values in item.covariates.items()
            }
            predictions: dict[str, Forecast] = {}
            for forecaster in forecasters:
                forecast = forecaster.predict(
                    history,
                    horizon,
                    future_dates=future_dates,
                    future_covariates=future_covariates,
                    quantiles=quantiles,
                )
                predictions[forecaster.name] = forecast
            records.append(
                BacktestRecord(
                    sku=item.sku,
                    segment=segment,
                    origin=future_dates[0],
                    actual=item.values[origin : origin + horizon].copy(),
                    forecasts=predictions,
                )
            )
    if not records:
        raise ValueError("no backtest windows were generated; provide more history or lower min_train")
    return records


def temporal_tune_test_split(
    records: Sequence[BacktestRecord], tune_fraction: float = 0.6
) -> tuple[list[BacktestRecord], list[BacktestRecord]]:
    if not 0.2 <= tune_fraction <= 0.8:
        raise ValueError("tune_fraction must be between 0.2 and 0.8")
    grouped: dict[str, list[BacktestRecord]] = {}
    for record in records:
        grouped.setdefault(record.sku, []).append(record)
    tune: list[BacktestRecord] = []
    test: list[BacktestRecord] = []
    for sku_records in grouped.values():
        ordered = sorted(sku_records, key=lambda record: record.origin)
        cut = min(max(int(len(ordered) * tune_fraction), 1), len(ordered) - 1)
        tune.extend(ordered[:cut])
        test.extend(ordered[cut:])
    return tune, test


def make_fused_forecasts(
    records: Sequence[BacktestRecord], fusion: AdaptiveFusion
) -> dict[tuple[str, str], Forecast]:
    return {
        (record.sku, str(record.origin)): fusion.blend(
            record.sku, record.segment, record.forecasts
        )
        for record in records
    }
