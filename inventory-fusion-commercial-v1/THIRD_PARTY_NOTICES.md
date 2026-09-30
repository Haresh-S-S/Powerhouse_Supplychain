# Third-Party Notices

Copyright and license notices for the original code in this repository are governed by the included Apache License 2.0.

The project interoperates with the following independently distributed model repositories. Their weights, code, model cards, documentation, names, and trademarks remain governed by their respective upstream terms. This repository does not relicense them.

| Component | Pinned revision | Declared license | Use in this project |
|---|---|---|---|
| `ibm-granite/granite-timeseries-ttm-r2` | `caa1eb3d16f053859d81952a1f387d6aeb670076` | Apache-2.0 | TTM R2.1 daily demand expert |
| `amazon/chronos-2` | `29ec3766d36d6f73f0696f85560a422f50e8498c` | Apache-2.0 | Covariate-aware probabilistic expert |
| `google/timesfm-2.5-200m-pytorch` | `1d952420fba87f3c6dee4f240de0f1a0fbc790e3` | Apache-2.0 | Long-context quantile expert |
| `Salesforce/moirai-2.0-R-small` | `30f43ff08c8494f4943ae1521e9d4e94a0fbb389` | CC BY-NC 4.0 | Recorded for comparison but explicitly blocked in commercial mode |

The approved base-model weights are downloaded directly from their official Hugging Face repositories and are not included in this source release. Full commit hashes are stored in `configs/model_registry.json`. `ModelRegistry.require_commercial()` and `scripts/download_models.py` enforce the license allowlist and revision pins before use.

Important compliance points:

- Preserve the Apache-2.0 license, applicable upstream copyright statements, attribution, and any upstream NOTICE content when redistributing covered material.
- Recheck the upstream repository and dependency tree before shipping a modified binary, hosted service, embedded product, or model bundle.
- Dataset licenses are separate from model and code licenses. No enterprise dataset is distributed in this repository.
- Product names and trademarks are used only to identify compatible upstream projects and do not imply endorsement.
- The Moirai entry is intentionally not part of the commercial expert pool.

This notice is an engineering compliance record, not legal advice. Obtain qualified legal review for the final distribution and deployment context.
