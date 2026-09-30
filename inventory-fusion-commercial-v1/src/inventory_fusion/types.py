from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

import numpy as np

DEFAULT_QUANTILES = (0.1, 0.5, 0.9)


@dataclass(slots=True)
class TimeSeries:
    sku: str
    dates: np.ndarray
    values: np.ndarray
    covariates: dict[str, np.ndarray] = field(default_factory=dict)
    location: str = "default"

    def __post_init__(self) -> None:
        self.dates = np.asarray(self.dates, dtype="datetime64[D]")
        self.values = np.asarray(self.values, dtype=float)
        if self.dates.ndim != 1 or self.values.ndim != 1:
            raise ValueError("dates and values must be one-dimensional")
        if len(self.dates) != len(self.values):
            raise ValueError("dates and values must have the same length")
        if len(self.values) == 0:
            raise ValueError("a time series cannot be empty")
        if np.any(~np.isfinite(self.values)) or np.any(self.values < 0):
            raise ValueError("demand values must be finite and non-negative")
        for name, values in list(self.covariates.items()):
            array = np.asarray(values)
            if len(array) != len(self.values):
                raise ValueError(f"covariate {name!r} does not match series length")
            self.covariates[name] = array

    def slice(self, start: int | None = None, end: int | None = None) -> TimeSeries:
        return TimeSeries(
            sku=self.sku,
            dates=self.dates[slice(start, end)],
            values=self.values[slice(start, end)],
            covariates={k: v[slice(start, end)] for k, v in self.covariates.items()},
            location=self.location,
        )


@dataclass(slots=True)
class Forecast:
    model_name: str
    sku: str
    values: dict[float, np.ndarray]
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized: dict[float, np.ndarray] = {}
        horizon: int | None = None
        for quantile, values in self.values.items():
            q = float(quantile)
            if not 0 < q < 1:
                raise ValueError(f"invalid quantile: {q}")
            array = np.asarray(values, dtype=float)
            if array.ndim != 1 or np.any(~np.isfinite(array)):
                raise ValueError("forecast values must be finite one-dimensional arrays")
            if horizon is None:
                horizon = len(array)
            elif len(array) != horizon:
                raise ValueError("all forecast quantiles must have equal horizon")
            normalized[q] = np.maximum(array, 0.0)
        if not normalized:
            raise ValueError("forecast must contain at least one quantile")
        ordered = sorted(normalized)
        matrix = np.vstack([normalized[q] for q in ordered])
        matrix = np.maximum.accumulate(matrix, axis=0)
        self.values = {q: matrix[i] for i, q in enumerate(ordered)}

    @property
    def horizon(self) -> int:
        return len(next(iter(self.values.values())))

    def quantile(self, q: float) -> np.ndarray:
        q = float(q)
        if q in self.values:
            return self.values[q]
        levels = np.asarray(sorted(self.values), dtype=float)
        matrix = np.vstack([self.values[level] for level in levels])
        if q <= levels[0]:
            return matrix[0].copy()
        if q >= levels[-1]:
            return matrix[-1].copy()
        upper = int(np.searchsorted(levels, q))
        lower = upper - 1
        ratio = (q - levels[lower]) / (levels[upper] - levels[lower])
        return matrix[lower] * (1 - ratio) + matrix[upper] * ratio

    @classmethod
    def from_point(
        cls,
        model_name: str,
        sku: str,
        point: np.ndarray,
        residuals: np.ndarray | None = None,
        quantiles: tuple[float, ...] = DEFAULT_QUANTILES,
        metadata: Mapping[str, object] | None = None,
    ) -> Forecast:
        point = np.maximum(np.asarray(point, dtype=float), 0.0)
        residuals = np.asarray(residuals if residuals is not None else [0.0], dtype=float)
        residuals = residuals[np.isfinite(residuals)]
        if residuals.size < 3:
            scale = max(float(np.mean(point)) * 0.15, 1.0)
            residuals = np.asarray([-scale, 0.0, scale])
        values = {q: point + float(np.quantile(residuals, q)) for q in quantiles}
        return cls(model_name=model_name, sku=sku, values=values, metadata=dict(metadata or {}))


@dataclass(slots=True)
class BacktestRecord:
    sku: str
    segment: str
    origin: np.datetime64
    actual: np.ndarray
    forecasts: dict[str, Forecast]


def ensure_quantiles(
    values: Mapping[float, np.ndarray], quantiles: tuple[float, ...] = DEFAULT_QUANTILES
) -> dict[float, np.ndarray]:
    temp = Forecast(model_name="normalize", sku="normalize", values=dict(values))
    return {q: temp.quantile(q) for q in quantiles}
