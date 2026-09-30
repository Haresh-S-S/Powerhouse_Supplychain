# Inventory Fusion backtest summary

- Holdout windows: 36
- Best single model: chronos_2 (WAPE 0.0841)
- Adaptive fusion WAPE: 0.0826
- Relative WAPE change vs best single: +1.76%
- This inventory cost is a backtest proxy, not a production ROI claim.

## Aggregate forecast metrics

| sku | model | wape | bias | rmse | pinball | p90_coverage | observations |
|---|---|---|---|---|---|---|---|
| __ALL__ | adaptive_fusion | 0.0826 | -0.0321 | 7.3866 | 0.1058 | 0.9147 | 504 |
| __ALL__ | chronos_2 | 0.0841 | -0.0275 | 7.3722 | 0.1259 | 0.9087 | 504 |
| __ALL__ | timesfm_2_5 | 0.0895 | -0.0403 | 7.5630 | 0.1030 | 0.9127 | 504 |
| __ALL__ | ttm_r2_1_daily | 0.1012 | -0.0552 | 7.7082 | 0.1369 | 0.9048 | 504 |
| __ALL__ | calendar_ridge | 0.1072 | -0.0554 | 7.6232 | 0.1442 | 0.7956 | 504 |
| __ALL__ | seasonal_naive_7 | 0.1308 | -0.0071 | 8.8323 | 0.2451 | 0.9246 | 504 |

## Inventory proxy metrics

| model | fill_rate | avg_leftover | proxy_total_cost | shortage_units |
|---|---|---|---|---|
| adaptive_fusion | 1.0000 | 60.0042 | 432.0303 | 0.0000 |
| timesfm_2_5 | 1.0000 | 60.1341 | 432.9656 | 0.0000 |
| chronos_2 | 1.0000 | 79.1390 | 569.8010 | 0.0000 |
| calendar_ridge | 0.9965 | 82.3650 | 816.3986 | 44.6742 |
| ttm_r2_1_daily | 1.0000 | 113.9124 | 820.1693 | 0.0000 |
| seasonal_naive_7 | 1.0000 | 131.0522 | 943.5760 | 0.0000 |