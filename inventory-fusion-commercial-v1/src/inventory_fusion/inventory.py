from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from inventory_fusion.types import Forecast


@dataclass(slots=True)
class InventoryPosition:
    sku: str
    on_hand: float
    on_order: float = 0.0
    allocated: float = 0.0
    backorders: float = 0.0
    lead_time_days: int = 7
    review_period_days: int = 7
    moq: int = 0
    case_pack: int = 1
    unit_cost: float = 1.0
    unit_volume: float = 1.0
    shortage_cost: float = 5.0
    holding_cost: float = 0.2

    @property
    def net_position(self) -> float:
        return self.on_hand + self.on_order - self.allocated - self.backorders


@dataclass(slots=True)
class ReplenishmentRecommendation:
    sku: str
    target_stock: float
    inventory_position: float
    unconstrained_quantity: int
    recommended_quantity: int
    expected_cost: float
    expected_volume: float
    constrained: bool
    reason: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _round_order(raw: float, moq: int, case_pack: int) -> int:
    if raw <= 0:
        return 0
    case_pack = max(int(case_pack), 1)
    quantity = int(np.ceil(raw / case_pack) * case_pack)
    if moq > 0 and quantity < moq:
        quantity = int(np.ceil(moq / case_pack) * case_pack)
    return quantity


def base_recommendation(
    forecast: Forecast,
    position: InventoryPosition,
    *,
    service_quantile: float = 0.9,
) -> ReplenishmentRecommendation:
    protection = position.lead_time_days + position.review_period_days
    if protection > forecast.horizon:
        raise ValueError(
            f"forecast horizon {forecast.horizon} is shorter than protection period {protection}"
        )
    target = float(np.sum(forecast.quantile(service_quantile)[:protection]))
    raw = max(target - position.net_position, 0.0)
    quantity = _round_order(raw, position.moq, position.case_pack)
    return ReplenishmentRecommendation(
        sku=position.sku,
        target_stock=target,
        inventory_position=position.net_position,
        unconstrained_quantity=quantity,
        recommended_quantity=quantity,
        expected_cost=quantity * position.unit_cost,
        expected_volume=quantity * position.unit_volume,
        constrained=False,
        reason="target service quantile after MOQ and case-pack rounding",
    )


def optimize_portfolio(
    forecasts: dict[str, Forecast],
    positions: dict[str, InventoryPosition],
    *,
    budget: float | None = None,
    capacity: float | None = None,
    service_quantile: float = 0.9,
) -> list[ReplenishmentRecommendation]:
    base = {
        sku: base_recommendation(forecast, positions[sku], service_quantile=service_quantile)
        for sku, forecast in forecasts.items()
    }
    total_cost = sum(item.expected_cost for item in base.values())
    total_volume = sum(item.expected_volume for item in base.values())
    if (budget is None or total_cost <= budget) and (capacity is None or total_volume <= capacity):
        return list(base.values())

    try:
        from ortools.linear_solver import pywraplp
    except ImportError:
        return _greedy_portfolio(base, positions, budget=budget, capacity=capacity)

    solver = pywraplp.Solver.CreateSolver("SCIP")
    if solver is None:
        return _greedy_portfolio(base, positions, budget=budget, capacity=capacity)

    variables = {}
    active = {}
    for sku, recommendation in base.items():
        position = positions[sku]
        pack = max(position.case_pack, 1)
        max_lots = int(np.ceil(recommendation.unconstrained_quantity / pack))
        variables[sku] = solver.IntVar(0, max_lots, f"lots_{sku}")
        active[sku] = solver.BoolVar(f"active_{sku}")
        solver.Add(variables[sku] <= max_lots * active[sku])
        min_lots = int(np.ceil(position.moq / pack)) if position.moq > 0 else 1
        solver.Add(variables[sku] >= min_lots * active[sku])

    if budget is not None:
        solver.Add(
            sum(
                variables[sku] * max(positions[sku].case_pack, 1) * positions[sku].unit_cost
                for sku in variables
            )
            <= budget
        )
    if capacity is not None:
        solver.Add(
            sum(
                variables[sku]
                * max(positions[sku].case_pack, 1)
                * positions[sku].unit_volume
                for sku in variables
            )
            <= capacity
        )

    objective = solver.Objective()
    for sku, variable in variables.items():
        position = positions[sku]
        pack = max(position.case_pack, 1)
        marginal_value = max(position.shortage_cost - position.holding_cost, 0.01)
        objective.SetCoefficient(variable, marginal_value * pack)
    objective.SetMaximization()
    status = solver.Solve()
    if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        return _greedy_portfolio(base, positions, budget=budget, capacity=capacity)

    result = []
    for sku, recommendation in base.items():
        position = positions[sku]
        quantity = round(variables[sku].solution_value()) * max(position.case_pack, 1)
        constrained = quantity != recommendation.unconstrained_quantity
        result.append(
            ReplenishmentRecommendation(
                sku=sku,
                target_stock=recommendation.target_stock,
                inventory_position=recommendation.inventory_position,
                unconstrained_quantity=recommendation.unconstrained_quantity,
                recommended_quantity=quantity,
                expected_cost=quantity * position.unit_cost,
                expected_volume=quantity * position.unit_volume,
                constrained=constrained,
                reason="portfolio optimization under budget/capacity" if constrained else recommendation.reason,
            )
        )
    return result


def _greedy_portfolio(
    base: dict[str, ReplenishmentRecommendation],
    positions: dict[str, InventoryPosition],
    *,
    budget: float | None,
    capacity: float | None,
) -> list[ReplenishmentRecommendation]:
    remaining_budget = float("inf") if budget is None else budget
    remaining_capacity = float("inf") if capacity is None else capacity
    ranked = sorted(
        base,
        key=lambda sku: positions[sku].shortage_cost / max(positions[sku].unit_cost, 1e-6),
        reverse=True,
    )
    result = []
    for sku in ranked:
        item = base[sku]
        position = positions[sku]
        pack = max(position.case_pack, 1)
        affordable = int(remaining_budget // max(position.unit_cost * pack, 1e-8)) * pack
        storable = int(remaining_capacity // max(position.unit_volume * pack, 1e-8)) * pack
        quantity = min(item.unconstrained_quantity, affordable, storable)
        if 0 < quantity < position.moq:
            quantity = 0
        quantity = int(quantity // pack * pack)
        remaining_budget -= quantity * position.unit_cost
        remaining_capacity -= quantity * position.unit_volume
        constrained = quantity != item.unconstrained_quantity
        result.append(
            ReplenishmentRecommendation(
                sku=sku,
                target_stock=item.target_stock,
                inventory_position=item.inventory_position,
                unconstrained_quantity=item.unconstrained_quantity,
                recommended_quantity=quantity,
                expected_cost=quantity * position.unit_cost,
                expected_volume=quantity * position.unit_volume,
                constrained=constrained,
                reason="greedy fallback under budget/capacity" if constrained else item.reason,
            )
        )
    return result
