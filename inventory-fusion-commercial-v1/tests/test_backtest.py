from inventory_fusion.backtest import (
    make_fused_forecasts,
    rolling_backtest,
    temporal_tune_test_split,
)
from inventory_fusion.cli import default_forecasters
from inventory_fusion.data import synthetic_inventory_series
from inventory_fusion.fusion import AdaptiveFusion


def test_synthetic_end_to_end():
    series = synthetic_inventory_series(n_skus=6, n_days=240, seed=7)
    records = rolling_backtest(
        series,
        default_forecasters(),
        horizon=7,
        min_train=140,
        step=14,
    )
    tune, test = temporal_tune_test_split(records)
    fusion = AdaptiveFusion().fit(tune)
    fused = make_fused_forecasts(test, fusion)
    assert len(fused) == len(test)
    assert all(forecast.horizon == 7 for forecast in fused.values())
