import pytest

from inventory_fusion.registry import CommercialLicenseError, ModelRegistry


def test_commercial_gate_allows_pinned_models_and_blocks_noncommercial():
    registry = ModelRegistry.load()
    approved = registry.require_commercial(
        ["ttm_r2_1_daily", "chronos_2", "timesfm_2_5"]
    )
    assert len(approved) == 3
    with pytest.raises(CommercialLicenseError, match="blocked"):
        registry.require_commercial(["moirai_2"])

