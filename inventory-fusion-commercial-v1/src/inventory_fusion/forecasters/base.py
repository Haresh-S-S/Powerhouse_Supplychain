from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping

import numpy as np

from inventory_fusion.types import DEFAULT_QUANTILES, Forecast, TimeSeries


class Forecaster(ABC):
    name: str

    def fit(self, series: list[TimeSeries]) -> Forecaster:
        return self

    @abstractmethod
    def predict(
        self,
        history: TimeSeries,
        horizon: int,
        *,
        future_dates: np.ndarray | None = None,
        future_covariates: Mapping[str, np.ndarray] | None = None,
        quantiles: tuple[float, ...] = DEFAULT_QUANTILES,
    ) -> Forecast:
        raise NotImplementedError

    def close(self) -> None:
        """Release optional model resources."""


def future_daily_dates(history: TimeSeries, horizon: int) -> np.ndarray:
    if horizon <= 0:
        raise ValueError("horizon must be positive")
    start = history.dates[-1] + np.timedelta64(1, "D")
    return start + np.arange(horizon).astype("timedelta64[D]")


def validate_future_dates(
    history: TimeSeries, horizon: int, future_dates: np.ndarray | None
) -> np.ndarray:
    if future_dates is None:
        return future_daily_dates(history, horizon)
    array = np.asarray(future_dates, dtype="datetime64[D]")
    if array.ndim != 1 or len(array) != horizon:
        raise ValueError("future_dates must match the requested horizon")
    return array

