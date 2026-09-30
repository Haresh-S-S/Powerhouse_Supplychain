# Enterprise Data Contract

This document defines the minimum input contract for a trustworthy inventory-forecasting backtest. Daily granularity is the default, and each row represents one SKU-location-date observation.

## Minimum CSV schema

| Column | Type | Required | Meaning |
|---|---|---:|---|
| `date` | ISO date | yes | Business date in one consistent local timezone |
| `sku` | string | yes | Stable SKU identifier |
| `location` | string | recommended | Warehouse or store identifier; use one fixed value for a single-site pilot |
| `demand` | non-negative number | yes | Best available estimate of requested demand, not blindly observed sales |
| `sales` | non-negative number | recommended | Fulfilled units |
| `ordered_units` | non-negative number | recommended | Customer-requested units before fulfillment limits |
| `stockout` | 0/1 | strongly recommended | Whether availability constrained sales during the period |
| `backorders` | non-negative number | recommended | Known unfulfilled requested units |
| `returns` | number | recommended | Returned units, stored separately from demand |
| `on_hand` | non-negative number | recommended | End-of-period usable inventory |
| `inbound_confirmed` | non-negative number | recommended | Quantity already ordered and confirmed |
| `allocated` | non-negative number | recommended | Inventory reserved for other demand |
| `price` | number | optional | Effective unit selling price known at the forecast origin |
| `promo` | 0/1 or number | optional | Promotion indicator or intensity |
| `holiday` | 0/1 | optional | Calendar event known in advance |
| `category` | string | optional | Stable product grouping for analysis and pooled learning |

The packaged loader requires at least `date`, `sku`, and `demand`. Extend the loader for `location` if the same SKU exists at multiple replenishment nodes; the effective series key should then be `sku + location`.

## Demand reconstruction

Use the best information available in this priority order:

1. customer-requested quantity, including known backorders;
2. fulfilled sales plus credible lost-sales estimates;
3. observed sales with stockout periods explicitly marked as censored;
4. observed sales alone only as a temporary baseline, with the limitation disclosed.

Do not interpret zero sales during a stockout as zero demand. A conservative first implementation may exclude censored target rows from the training loss while retaining them in the input history with an availability flag.

## Time and leakage rules

- Sort by series key and date; reject duplicate keys unless an explicit aggregation rule exists.
- Reindex to a complete daily calendar and distinguish a true zero from a missing record.
- Build rolling samples using only information available at each forecast origin.
- A future promotion is valid only if it had been approved and visible to planners at that origin.
- Use promised lead time as known at the order date; never substitute the later realized receipt date as a historical feature.
- Fit imputers, scalers, encoders, fusion weights, and hyperparameters on training/tuning periods only.
- Seal the final holdout period before model selection.
- Preserve cancellations, returns, substitutions, and unit-of-measure conversions as separate auditable transformations.

## Inventory decision fields

For replenishment optimization, provide a current snapshot with:

| Field | Meaning |
|---|---|
| `available_inventory` | Usable on-hand quantity |
| `confirmed_inbound` | Purchase quantities with reliable arrival commitments |
| `allocated_inventory` | Stock reserved for existing orders |
| `backorders` | Unfulfilled demand owed to customers |
| `review_period_days` | Time until the next planned replenishment review |
| `lead_time_days` | Supplier lead-time assumption and preferably its uncertainty |
| `moq` | Minimum order quantity |
| `case_pack` | Required order multiple |
| `unit_cost` | Purchase cost used by the optimization objective and budget |
| `unit_volume` | Warehouse-capacity consumption |
| `holding_cost` | Cost of carrying one unit for the modeled period |
| `shortage_cost` | Explicit business penalty for one unit of unmet demand |

Every optimization run should persist the forecast revision, input snapshot, constraint values, proposed quantity, manual override, approver, and eventual outcome.

## Acceptance checks

Before training, report date coverage, missing days, duplicates, invalid quantities, stockout/censoring frequency, history length, non-zero demand days, late-arriving data, promotion and price coverage, unit-of-measure consistency, and the exact train/tune/holdout boundaries.

A model score is not trustworthy until these data-quality checks are reproducible.
