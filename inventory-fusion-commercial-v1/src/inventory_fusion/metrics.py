from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from inventory_fusion.types import DEFAULT_QUANTILES, BacktestRecord, Forecast


def pinball_loss(actual: np.ndarray, predicted: np.ndarray, quantile: float) -> float:
    error = np.asarray(actual, dtype=float) - np.asarray(predicted, dtype=float)
    return float(np.mean(np.maximum(quantile * error, (quantile - 1.0) * error)))


def normalized_pinball(
    actual: np.ndarray,
    forecast: Forecast,
    quantiles: tuple[float, ...] = DEFAULT_QUANTILES,
) -> float:
    scale = max(float(np.mean(np.abs(actual))), 1.0)
    return float(np.mean([pinball_loss(actual, forecast.quantile(q), q) for q in quantiles])) / scale


def forecast_metrics(actual: np.ndarray, forecast: Forecast) -> dict[str, float]:
    actual = np.asarray(actual, dtype=float)
    p50 = forecast.quantile(0.5)
    denominator = max(float(np.sum(np.abs(actual))), 1.0)
    return {
        "wape": float(np.sum(np.abs(actual - p50)) / denominator),
        "bias": float(np.sum(p50 - actual) / denominator),
        "rmse": float(np.sqrt(np.mean(np.square(actual - p50)))),
        "pinball": normalized_pinball(actual, forecast),
        "p90_coverage": float(np.mean(actual <= forecast.quantile(0.9))),
    }


def summarize_records(
    records: Iterable[BacktestRecord],
    fused_forecasts: dict[tuple[str, str], Forecast] | None = None,
) -> list[dict[str, object]]:
    buckets: dict[tuple[str, str], list[tuple[np.ndarray, Forecast]]] = {}
    for record in records:
        for model_name, forecast in record.forecasts.items():
            buckets.setdefault((record.sku, model_name), []).append((record.actual, forecast))
        if fused_forecasts is not None:
            key = (record.sku, str(record.origin))
            if key in fused_forecasts:
                forecast = fused_forecasts[key]
                buckets.setdefault((record.sku, forecast.model_name), []).append(
                    (record.actual, forecast)
                )

    rows: list[dict[str, object]] = []
    all_model_buckets: dict[str, list[tuple[np.ndarray, Forecast]]] = {}
    for (sku, model_name), values in sorted(buckets.items()):
        all_model_buckets.setdefault(model_name, []).extend(values)
        rows.append(_summarize_bucket(sku, model_name, values))
    for model_name, values in sorted(all_model_buckets.items()):
        rows.append(_summarize_bucket("__ALL__", model_name, values))
    return rows


def _summarize_bucket(
    sku: str, model_name: str, values: list[tuple[np.ndarray, Forecast]]
) -> dict[str, object]:
    actual = np.concatenate([item[0] for item in values])
    p50 = np.concatenate([item[1].quantile(0.5) for item in values])
    p90 = np.concatenate([item[1].quantile(0.9) for item in values])
    denominator = max(float(np.sum(np.abs(actual))), 1.0)
    pinballs = [normalized_pinball(item_actual, item_forecast) for item_actual, item_forecast in values]
    return {
        "sku": sku,
        "model": model_name,
        "wape": float(np.sum(np.abs(actual - p50)) / denominator),
        "bias": float(np.sum(p50 - actual) / denominator),
        "rmse": float(np.sqrt(np.mean(np.square(actual - p50)))),
        "pinball": float(np.mean(pinballs)),
        "p90_coverage": float(np.mean(actual <= p90)),
        "observations": int(actual.size),
    }

