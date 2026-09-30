from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from inventory_fusion.types import TimeSeries

REQUIRED_COLUMNS = {"date", "sku", "demand"}


def load_inventory_csv(path: str | Path) -> list[TimeSeries]:
    frame = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")
    frame["date"] = pd.to_datetime(frame["date"], errors="raise").dt.normalize()
    frame["demand"] = pd.to_numeric(frame["demand"], errors="raise")
    if frame["demand"].isna().any() or (frame["demand"] < 0).any():
        raise ValueError("demand must be non-negative and cannot be missing")
    if "location" not in frame:
        frame["location"] = "default"
    duplicate = frame.duplicated(["sku", "location", "date"])
    if duplicate.any():
        raise ValueError("duplicate sku/location/date rows found")

    known_non_covariates = {
        "date",
        "sku",
        "location",
        "demand",
        "inventory",
        "on_order",
        "allocated",
        "backorders",
        "lead_time_days",
        "review_period_days",
        "moq",
        "case_pack",
        "unit_cost",
        "unit_volume",
    }
    covariate_columns = [
        column
        for column in frame.columns
        if column not in known_non_covariates and pd.api.types.is_numeric_dtype(frame[column])
    ]
    result: list[TimeSeries] = []
    for (sku, location), group in frame.groupby(["sku", "location"], sort=True):
        group = group.sort_values("date")
        dates = group["date"].to_numpy(dtype="datetime64[D]")
        if len(dates) > 1 and np.any(np.diff(dates).astype("timedelta64[D]").astype(int) != 1):
            raise ValueError(f"{sku}/{location} is not a contiguous daily series")
        result.append(
            TimeSeries(
                sku=str(sku),
                location=str(location),
                dates=dates,
                values=group["demand"].to_numpy(dtype=float),
                covariates={
                    name: group[name].fillna(0).to_numpy(dtype=float)
                    for name in covariate_columns
                },
            )
        )
    return result


def synthetic_inventory_series(
    *, n_skus: int = 18, n_days: int = 420, seed: int = 20260819
) -> list[TimeSeries]:
    rng = np.random.default_rng(seed)
    dates = np.datetime64("2025-01-01") + np.arange(n_days).astype("timedelta64[D]")
    day = np.arange(n_days, dtype=float)
    weekday = (dates.astype("datetime64[D]").astype(np.int64) + 3) % 7
    result: list[TimeSeries] = []
    kinds = ("seasonal", "trend", "intermittent", "stable", "mixed", "promotion")
    for index in range(n_skus):
        kind = kinds[index % len(kinds)]
        base = float(rng.uniform(12, 45))
        promo = (rng.random(n_days) < 0.08).astype(float)
        promo = np.maximum(promo, np.roll(promo, 1) * 0.7)
        price = 10.0 + rng.normal(0, 0.35, n_days) - promo * rng.uniform(0.8, 1.8)
        noise = rng.normal(0, max(base * 0.09, 1.2), n_days)
        weekly = np.take(np.asarray([0.78, 0.86, 0.94, 1.0, 1.12, 1.32, 1.18]), weekday)
        if kind == "seasonal":
            demand = base * weekly + noise
        elif kind == "trend":
            demand = base + day * rng.uniform(0.025, 0.065) + noise
        elif kind == "intermittent":
            occurrence = rng.random(n_days) < (0.13 + promo * 0.12)
            demand = occurrence * rng.gamma(shape=2.2, scale=base / 2.2, size=n_days)
        elif kind == "stable":
            demand = base + noise * 0.65
        elif kind == "mixed":
            demand = base * weekly + day * rng.uniform(-0.015, 0.04) + noise
        else:
            demand = base * (1 + promo * rng.uniform(0.65, 1.2)) + noise
        demand = np.maximum(np.round(demand, 1), 0.0)
        result.append(
            TimeSeries(
                sku=f"SKU-{index + 1:03d}-{kind}",
                dates=dates.copy(),
                values=demand,
                covariates={"promo": promo, "price": price},
            )
        )
    return result
