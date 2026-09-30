import json

import numpy as np

from inventory_fusion.fusion import AdaptiveFusion
from inventory_fusion.types import BacktestRecord, Forecast


def _forecast(name: str, sku: str, values: list[float]) -> Forecast:
    point = np.asarray(values, dtype=float)
    return Forecast(
        model_name=name,
        sku=sku,
        values={0.1: point * 0.8, 0.5: point, 0.9: point * 1.2},
    )


def test_fusion_learns_different_sku_specialists(tmp_path):
    records = []
    for index in range(8):
        records.append(
            BacktestRecord(
                sku="stable",
                segment="regular",
                origin=np.datetime64("2026-01-01") + np.timedelta64(index, "D"),
                actual=np.asarray([10.0, 10.0]),
                forecasts={
                    "model_a": _forecast("model_a", "stable", [10.0, 10.0]),
                    "model_b": _forecast("model_b", "stable", [20.0, 20.0]),
                },
            )
        )
        records.append(
            BacktestRecord(
                sku="trend",
                segment="trending",
                origin=np.datetime64("2026-01-01") + np.timedelta64(index, "D"),
                actual=np.asarray([20.0, 20.0]),
                forecasts={
                    "model_a": _forecast("model_a", "trend", [10.0, 10.0]),
                    "model_b": _forecast("model_b", "trend", [20.0, 20.0]),
                },
            )
        )

    fusion = AdaptiveFusion().fit(records)
    assert fusion.sku_weights["stable"]["model_a"] > fusion.sku_weights["stable"]["model_b"]
    assert fusion.sku_weights["trend"]["model_b"] > fusion.sku_weights["trend"]["model_a"]
    blended = fusion.blend("stable", "regular", records[0].forecasts)
    assert blended.model_name == "adaptive_fusion"
    assert np.all(np.diff(np.vstack(list(blended.values.values())), axis=0) >= 0)

    state = tmp_path / "state.json"
    fusion.save(state)
    restored = AdaptiveFusion.load(state)
    assert restored.sku_weights == fusion.sku_weights
    assert json.loads(state.read_text(encoding="utf-8"))["schema_version"] == 1
