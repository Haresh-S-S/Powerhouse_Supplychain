from __future__ import annotations

from collections.abc import Mapping

import numpy as np

from inventory_fusion.forecasters.base import Forecaster, validate_future_dates
from inventory_fusion.types import DEFAULT_QUANTILES, Forecast, TimeSeries


def _moving_average_residuals(values: np.ndarray, window: int) -> np.ndarray:
    if len(values) <= window:
        return values - np.mean(values)
    predictions = np.asarray([np.mean(values[i - window : i]) for i in range(window, len(values))])
    return values[window:] - predictions


class SeasonalNaiveForecaster(Forecaster):
    def __init__(self, season_length: int = 7) -> None:
        if season_length <= 0:
            raise ValueError("season_length must be positive")
        self.season_length = season_length
        self.name = f"seasonal_naive_{season_length}"

    def predict(
        self,
        history: TimeSeries,
        horizon: int,
        *,
        future_dates: np.ndarray | None = None,
        future_covariates: Mapping[str, np.ndarray] | None = None,
        quantiles: tuple[float, ...] = DEFAULT_QUANTILES,
    ) -> Forecast:
        del future_dates, future_covariates
        values = history.values
        season = min(self.season_length, len(values))
        template = values[-season:]
        point = np.resize(template, horizon)
        residuals = values[season:] - values[:-season] if len(values) > season else None
        return Forecast.from_point(self.name, history.sku, point, residuals, quantiles)


class MovingAverageForecaster(Forecaster):
    def __init__(self, window: int = 28) -> None:
        if window <= 0:
            raise ValueError("window must be positive")
        self.window = window
        self.name = f"moving_average_{window}"

    def predict(
        self,
        history: TimeSeries,
        horizon: int,
        *,
        future_dates: np.ndarray | None = None,
        future_covariates: Mapping[str, np.ndarray] | None = None,
        quantiles: tuple[float, ...] = DEFAULT_QUANTILES,
    ) -> Forecast:
        del future_dates, future_covariates
        window = min(self.window, len(history.values))
        center = float(np.mean(history.values[-window:]))
        point = np.full(horizon, center)
        residuals = _moving_average_residuals(history.values, window)
        return Forecast.from_point(self.name, history.sku, point, residuals, quantiles)


class LinearTrendForecaster(Forecaster):
    def __init__(self, window: int = 84, damping: float = 0.9) -> None:
        self.window = window
        self.damping = damping
        self.name = "linear_trend"

    def predict(
        self,
        history: TimeSeries,
        horizon: int,
        *,
        future_dates: np.ndarray | None = None,
        future_covariates: Mapping[str, np.ndarray] | None = None,
        quantiles: tuple[float, ...] = DEFAULT_QUANTILES,
    ) -> Forecast:
        del future_dates, future_covariates
        values = history.values[-min(self.window, len(history.values)) :]
        x = np.arange(len(values), dtype=float)
        if len(values) < 2:
            slope, intercept = 0.0, float(values[-1])
        else:
            slope, intercept = np.polyfit(x, values, 1)
        steps = np.arange(1, horizon + 1, dtype=float)
        damped_steps = np.cumsum(np.power(self.damping, steps))
        point = intercept + slope * (len(values) - 1 + damped_steps)
        residuals = values - (intercept + slope * x)
        return Forecast.from_point(self.name, history.sku, point, residuals, quantiles)


class CrostonForecaster(Forecaster):
    def __init__(self, alpha: float = 0.15) -> None:
        if not 0 < alpha <= 1:
            raise ValueError("alpha must be in (0, 1]")
        self.alpha = alpha
        self.name = "croston_sba"

    def _level(self, values: np.ndarray) -> float:
        positive = np.flatnonzero(values > 0)
        if positive.size == 0:
            return 0.0
        z = float(values[positive[0]])
        p = float(positive[0] + 1)
        last = int(positive[0])
        for index in positive[1:]:
            interval = int(index) - last
            z += self.alpha * (float(values[index]) - z)
            p += self.alpha * (interval - p)
            last = int(index)
        return max((1 - self.alpha / 2) * z / max(p, 1e-6), 0.0)

    def predict(
        self,
        history: TimeSeries,
        horizon: int,
        *,
        future_dates: np.ndarray | None = None,
        future_covariates: Mapping[str, np.ndarray] | None = None,
        quantiles: tuple[float, ...] = DEFAULT_QUANTILES,
    ) -> Forecast:
        del future_dates, future_covariates
        point = np.full(horizon, self._level(history.values))
        warmup = min(28, max(2, len(history.values) // 4))
        residuals = []
        for end in range(warmup, len(history.values)):
            residuals.append(history.values[end] - self._level(history.values[:end]))
        return Forecast.from_point(
            self.name, history.sku, point, np.asarray(residuals), quantiles
        )


class CalendarRidgeForecaster(Forecaster):
    """Small global-style regressor using trend, calendar and known future covariates."""

    def __init__(self, ridge: float = 8.0, max_history: int = 365) -> None:
        self.ridge = ridge
        self.max_history = max_history
        self.name = "calendar_ridge"

    @staticmethod
    def _date_features(dates: np.ndarray) -> np.ndarray:
        days = dates.astype("datetime64[D]").astype(np.int64)
        weekday = (days + 3) % 7
        annual_phase = 2 * np.pi * days / 365.25
        weekly_phase = 2 * np.pi * weekday / 7.0
        return np.column_stack(
            [
                np.sin(weekly_phase),
                np.cos(weekly_phase),
                np.sin(annual_phase),
                np.cos(annual_phase),
            ]
        )

    @staticmethod
    def _scaled_covariate(
        history_values: np.ndarray,
        future_values: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        history_values = np.asarray(history_values, dtype=float)
        future_values = np.asarray(future_values, dtype=float)
        center = float(np.nanmean(history_values)) if history_values.size else 0.0
        scale = float(np.nanstd(history_values)) if history_values.size else 1.0
        scale = scale if scale > 1e-8 else 1.0
        return (
            np.nan_to_num((history_values - center) / scale),
            np.nan_to_num((future_values - center) / scale),
        )

    def predict(
        self,
        history: TimeSeries,
        horizon: int,
        *,
        future_dates: np.ndarray | None = None,
        future_covariates: Mapping[str, np.ndarray] | None = None,
        quantiles: tuple[float, ...] = DEFAULT_QUANTILES,
    ) -> Forecast:
        future_dates = validate_future_dates(history, horizon, future_dates)
        future_covariates = future_covariates or {}
        length = min(self.max_history, len(history.values))
        values = history.values[-length:]
        dates = history.dates[-length:]
        trend_history = np.linspace(-1.0, 0.0, length)
        trend_future = np.arange(1, horizon + 1, dtype=float) / max(length, 1)
        x_history = [np.ones(length), trend_history]
        x_future = [np.ones(horizon), trend_future]
        date_history = self._date_features(dates)
        date_future = self._date_features(future_dates)
        x_history.extend(date_history[:, i] for i in range(date_history.shape[1]))
        x_future.extend(date_future[:, i] for i in range(date_future.shape[1]))

        for name in ("promo", "price"):
            if name not in history.covariates:
                continue
            hist = np.asarray(history.covariates[name][-length:], dtype=float)
            fut = np.asarray(future_covariates.get(name, np.repeat(hist[-1], horizon)))
            if len(fut) != horizon:
                raise ValueError(f"future covariate {name!r} must match horizon")
            hist_scaled, fut_scaled = self._scaled_covariate(hist, fut)
            x_history.append(hist_scaled)
            x_future.append(fut_scaled)

        design = np.column_stack(x_history)
        future_design = np.column_stack(x_future)
        penalty = np.eye(design.shape[1]) * self.ridge
        penalty[0, 0] = 0.0
        beta = np.linalg.solve(design.T @ design + penalty, design.T @ values)
        fitted = design @ beta
        point = future_design @ beta
        residuals = values - fitted
        return Forecast.from_point(self.name, history.sku, point, residuals, quantiles)
