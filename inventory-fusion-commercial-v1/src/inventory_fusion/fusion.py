from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from inventory_fusion.metrics import normalized_pinball
from inventory_fusion.types import BacktestRecord, Forecast


class AdaptiveFusion:
    """Hierarchical adaptive ensemble with auditable per-SKU weights.

    Evidence is pooled at global, segment and SKU levels. New SKUs inherit segment
    weights; mature SKUs progressively rely on their own backtest history.
    """

    def __init__(
        self,
        *,
        temperature: float = 7.0,
        sku_shrinkage: float = 4.0,
        segment_shrinkage: float = 8.0,
        max_weight: float = 0.88,
    ) -> None:
        self.temperature = temperature
        self.sku_shrinkage = sku_shrinkage
        self.segment_shrinkage = segment_shrinkage
        self.max_weight = max_weight
        self.global_weights: dict[str, float] = {}
        self.segment_weights: dict[str, dict[str, float]] = {}
        self.sku_weights: dict[str, dict[str, float]] = {}
        self.sku_segments: dict[str, str] = {}
        self.loss_history: dict[str, dict[str, list[float]]] = {}

    @staticmethod
    def classify(values: np.ndarray, covariates: dict[str, np.ndarray] | None = None) -> str:
        values = np.asarray(values, dtype=float)
        zero_rate = float(np.mean(values <= 0))
        positive = values[values > 0]
        cv2 = float(np.square(np.std(positive) / max(np.mean(positive), 1e-6))) if positive.size else 0
        if zero_rate >= 0.45:
            return "intermittent"
        promo = None if covariates is None else covariates.get("promo")
        if promo is not None and np.any(np.asarray(promo) > 0):
            promo = np.asarray(promo, dtype=float)
            if np.mean(values[promo > 0]) > np.mean(values[promo <= 0]) * 1.25:
                return "promotion_driven"
        if len(values) >= 28:
            x = np.arange(len(values), dtype=float)
            slope = float(np.polyfit(x, values, 1)[0])
            if abs(slope) * len(values) > max(float(np.mean(values)) * 0.35, 2.0):
                return "trending"
        return "volatile" if cv2 > 0.7 else "regular"

    @staticmethod
    def _mean_losses(
        loss_lists: dict[str, list[float]], fallback: dict[str, float] | None = None
    ) -> dict[str, float]:
        result = dict(fallback or {})
        for model, values in loss_lists.items():
            if values:
                result[model] = float(np.mean(values))
        return result

    def _weights_from_losses(self, losses: dict[str, float]) -> dict[str, float]:
        clean = {name: max(float(loss), 1e-8) for name, loss in losses.items() if np.isfinite(loss)}
        if not clean:
            return {}
        best = min(clean.values())
        logits = {
            name: -self.temperature * (loss / max(best, 1e-8) - 1.0)
            for name, loss in clean.items()
        }
        peak = max(logits.values())
        raw = {name: float(np.exp(value - peak)) for name, value in logits.items()}
        total = sum(raw.values())
        weights = {name: value / total for name, value in raw.items()}
        if len(weights) > 1 and max(weights.values()) > self.max_weight:
            winner = max(weights, key=weights.get)
            remainder = 1.0 - self.max_weight
            other_total = sum(value for name, value in weights.items() if name != winner)
            weights = {
                name: self.max_weight
                if name == winner
                else remainder * value / max(other_total, 1e-12)
                for name, value in weights.items()
            }
        return weights

    def fit(self, records: list[BacktestRecord]) -> AdaptiveFusion:
        global_losses: dict[str, list[float]] = defaultdict(list)
        segment_losses: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        sku_losses: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        sku_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        segment_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

        for record in records:
            self.sku_segments[record.sku] = record.segment
            for model, forecast in record.forecasts.items():
                loss = normalized_pinball(record.actual, forecast)
                global_losses[model].append(loss)
                segment_losses[record.segment][model].append(loss)
                sku_losses[record.sku][model].append(loss)
                sku_counts[record.sku][model] += 1
                segment_counts[record.segment][model] += 1

        global_mean = self._mean_losses(global_losses)
        self.global_weights = self._weights_from_losses(global_mean)
        segment_means: dict[str, dict[str, float]] = {}
        for segment, losses in segment_losses.items():
            own = self._mean_losses(losses, global_mean)
            combined = {}
            for model in global_mean:
                count = segment_counts[segment].get(model, 0)
                combined[model] = (
                    own.get(model, global_mean[model]) * count
                    + global_mean[model] * self.segment_shrinkage
                ) / (count + self.segment_shrinkage)
            segment_means[segment] = combined
            self.segment_weights[segment] = self._weights_from_losses(combined)

        for sku, losses in sku_losses.items():
            segment = self.sku_segments[sku]
            prior = segment_means.get(segment, global_mean)
            own = self._mean_losses(losses, prior)
            combined = {}
            for model in global_mean:
                count = sku_counts[sku].get(model, 0)
                combined[model] = (
                    own.get(model, prior[model]) * count + prior[model] * self.sku_shrinkage
                ) / (count + self.sku_shrinkage)
            self.sku_weights[sku] = self._weights_from_losses(combined)
        self.loss_history = {
            sku: {model: list(values) for model, values in losses.items()}
            for sku, losses in sku_losses.items()
        }
        return self

    def weights_for(self, sku: str, segment: str, available: set[str]) -> dict[str, float]:
        candidates = self.sku_weights.get(
            sku, self.segment_weights.get(segment, self.global_weights)
        )
        weights = {name: value for name, value in candidates.items() if name in available}
        if not weights:
            return {name: 1.0 / len(available) for name in sorted(available)}
        total = sum(weights.values())
        return {name: value / total for name, value in weights.items()}

    def blend(self, sku: str, segment: str, forecasts: dict[str, Forecast]) -> Forecast:
        if not forecasts:
            raise ValueError("at least one model forecast is required")
        horizons = {forecast.horizon for forecast in forecasts.values()}
        if len(horizons) != 1:
            raise ValueError("all model forecasts must have the same horizon")
        levels = sorted({level for forecast in forecasts.values() for level in forecast.values})
        weights = self.weights_for(sku, segment, set(forecasts))
        values = {
            level: sum(weights[name] * forecasts[name].quantile(level) for name in weights)
            for level in levels
        }
        return Forecast(
            model_name="adaptive_fusion",
            sku=sku,
            values=values,
            metadata={"weights": weights, "segment": segment},
        )

    def online_update(self, record: BacktestRecord, learning_rate: float = 0.25) -> None:
        current = self.weights_for(record.sku, record.segment, set(record.forecasts))
        updated = {}
        for model, weight in current.items():
            loss = normalized_pinball(record.actual, record.forecasts[model])
            updated[model] = weight * float(np.exp(-learning_rate * loss))
            self.loss_history.setdefault(record.sku, {}).setdefault(model, []).append(loss)
        total = sum(updated.values())
        self.sku_weights[record.sku] = {name: value / total for name, value in updated.items()}
        self.sku_segments[record.sku] = record.segment

    def save(self, path: str | Path) -> None:
        payload = {
            "schema_version": 1,
            "temperature": self.temperature,
            "sku_shrinkage": self.sku_shrinkage,
            "segment_shrinkage": self.segment_shrinkage,
            "max_weight": self.max_weight,
            "global_weights": self.global_weights,
            "segment_weights": self.segment_weights,
            "sku_weights": self.sku_weights,
            "sku_segments": self.sku_segments,
            "loss_history": self.loss_history,
        }
        Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> AdaptiveFusion:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        instance = cls(
            temperature=payload["temperature"],
            sku_shrinkage=payload["sku_shrinkage"],
            segment_shrinkage=payload["segment_shrinkage"],
            max_weight=payload["max_weight"],
        )
        instance.global_weights = payload["global_weights"]
        instance.segment_weights = payload["segment_weights"]
        instance.sku_weights = payload["sku_weights"]
        instance.sku_segments = payload["sku_segments"]
        instance.loss_history = payload["loss_history"]
        return instance

    def weight_rows(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for model, weight in sorted(self.global_weights.items()):
            rows.append({"scope": "global", "key": "__ALL__", "model": model, "weight": weight})
        for segment, weights in sorted(self.segment_weights.items()):
            for model, weight in sorted(weights.items()):
                rows.append({"scope": "segment", "key": segment, "model": model, "weight": weight})
        for sku, weights in sorted(self.sku_weights.items()):
            for model, weight in sorted(weights.items()):
                rows.append({"scope": "sku", "key": sku, "model": model, "weight": weight})
        return rows

