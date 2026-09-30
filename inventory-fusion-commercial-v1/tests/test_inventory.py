import numpy as np

from inventory_fusion.inventory import InventoryPosition, base_recommendation, optimize_portfolio
from inventory_fusion.types import Forecast


def _forecast(sku: str, value: float) -> Forecast:
    return Forecast(
        model_name="test",
        sku=sku,
        values={
            0.1: np.full(14, value * 0.8),
            0.5: np.full(14, value),
            0.9: np.full(14, value * 1.2),
        },
    )


def test_recommendation_respects_moq_and_case_pack():
    position = InventoryPosition(sku="A", on_hand=30, moq=96, case_pack=12)
    recommendation = base_recommendation(_forecast("A", 5), position)
    assert recommendation.recommended_quantity == 96
    assert recommendation.recommended_quantity % 12 == 0


def test_portfolio_respects_budget():
    forecasts = {"A": _forecast("A", 10), "B": _forecast("B", 8)}
    positions = {
        "A": InventoryPosition(sku="A", on_hand=0, case_pack=10, unit_cost=2, shortage_cost=10),
        "B": InventoryPosition(sku="B", on_hand=0, case_pack=10, unit_cost=2, shortage_cost=4),
    }
    result = optimize_portfolio(forecasts, positions, budget=300)
    assert sum(item.expected_cost for item in result) <= 300 + 1e-6

