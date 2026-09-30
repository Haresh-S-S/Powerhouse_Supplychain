from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from inventory_fusion.fusion import AdaptiveFusion
from inventory_fusion.metrics import summarize_records
from inventory_fusion.types import BacktestRecord, Forecast


def inventory_proxy_metrics(
    records: list[BacktestRecord], fused: dict[tuple[str, str], Forecast]
) -> pd.DataFrame:
    buckets: dict[str, dict[str, float]] = {}
    for record in records:
        forecasts = dict(record.forecasts)
        forecasts["adaptive_fusion"] = fused[(record.sku, str(record.origin))]
        actual_total = float(np.sum(record.actual))
        for model, forecast in forecasts.items():
            order_up_to = float(np.sum(forecast.quantile(0.9)))
            shortage = max(actual_total - order_up_to, 0.0)
            leftover = max(order_up_to - actual_total, 0.0)
            bucket = buckets.setdefault(
                model,
                {"demand": 0.0, "shortage": 0.0, "leftover": 0.0, "cost": 0.0, "windows": 0.0},
            )
            bucket["demand"] += actual_total
            bucket["shortage"] += shortage
            bucket["leftover"] += leftover
            bucket["cost"] += shortage * 5.0 + leftover * 0.2
            bucket["windows"] += 1
    rows = []
    for model, values in buckets.items():
        rows.append(
            {
                "model": model,
                "fill_rate": 1.0 - values["shortage"] / max(values["demand"], 1.0),
                "avg_leftover": values["leftover"] / max(values["windows"], 1.0),
                "proxy_total_cost": values["cost"],
                "shortage_units": values["shortage"],
            }
        )
    return pd.DataFrame(rows).sort_values("proxy_total_cost")


def write_report(
    output_dir: str | Path,
    records: list[BacktestRecord],
    fusion: AdaptiveFusion,
    fused: dict[tuple[str, str], Forecast],
) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    metrics = pd.DataFrame(summarize_records(records, fused))
    weights = pd.DataFrame(fusion.weight_rows())
    inventory = inventory_proxy_metrics(records, fused)
    metrics_path = output / "forecast_metrics.csv"
    weights_path = output / "fusion_weights.csv"
    inventory_path = output / "inventory_proxy_metrics.csv"
    metrics.to_csv(metrics_path, index=False, encoding="utf-8-sig")
    weights.to_csv(weights_path, index=False, encoding="utf-8-sig")
    inventory.to_csv(inventory_path, index=False, encoding="utf-8-sig")
    fusion.save(output / "fusion_state.json")

    aggregate = metrics[metrics["sku"] == "__ALL__"].sort_values("wape")
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    colors = ["#0f766e" if name == "adaptive_fusion" else "#94a3b8" for name in aggregate["model"]]
    axes[0].barh(aggregate["model"], aggregate["wape"], color=colors)
    axes[0].invert_yaxis()
    axes[0].set_title("Rolling holdout WAPE (lower is better)")
    axes[0].set_xlabel("WAPE")
    inventory_plot = inventory.sort_values("proxy_total_cost")
    cost_colors = ["#7c3aed" if name == "adaptive_fusion" else "#c4b5fd" for name in inventory_plot["model"]]
    axes[1].barh(inventory_plot["model"], inventory_plot["proxy_total_cost"], color=cost_colors)
    axes[1].invert_yaxis()
    axes[1].set_title("Inventory proxy cost (lower is better)")
    axes[1].set_xlabel("holding + shortage cost")
    fig.tight_layout()
    comparison_path = output / "model_comparison.png"
    fig.savefig(comparison_path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    sample = max(records, key=lambda record: float(np.sum(record.actual)))
    sample_fused = fused[(sample.sku, str(sample.origin))]
    x = np.arange(len(sample.actual))
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(x, sample.actual, color="#111827", linewidth=2.2, marker="o", label="actual")
    for name, forecast in sample.forecasts.items():
        ax.plot(x, forecast.quantile(0.5), linewidth=1.1, alpha=0.55, label=name)
    ax.plot(x, sample_fused.quantile(0.5), color="#7c3aed", linewidth=2.5, label="adaptive_fusion")
    ax.fill_between(
        x,
        sample_fused.quantile(0.1),
        sample_fused.quantile(0.9),
        color="#c4b5fd",
        alpha=0.35,
        label="fusion P10-P90",
    )
    ax.set_title(f"Forecast evidence: {sample.sku} at {sample.origin}")
    ax.set_xlabel("forecast day")
    ax.set_ylabel("demand")
    ax.legend(ncol=2, fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    evidence_path = output / "forecast_evidence.png"
    fig.savefig(evidence_path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    sku_weights = weights[weights["scope"] == "sku"]
    pivot = sku_weights.pivot(index="key", columns="model", values="weight").fillna(0)
    fig, ax = plt.subplots(figsize=(10, max(5, len(pivot) * 0.34)))
    image = ax.imshow(pivot.to_numpy(), aspect="auto", cmap="YlGnBu", vmin=0, vmax=1)
    ax.set_xticks(range(len(pivot.columns)), pivot.columns, rotation=35, ha="right")
    ax.set_yticks(range(len(pivot.index)), pivot.index)
    ax.set_title("Learned model weights by SKU")
    fig.colorbar(image, ax=ax, label="weight")
    fig.tight_layout()
    weights_plot_path = output / "learned_weights.png"
    fig.savefig(weights_plot_path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    best_single = aggregate[aggregate["model"] != "adaptive_fusion"].iloc[0]
    fused_row = aggregate[aggregate["model"] == "adaptive_fusion"].iloc[0]
    lift = (float(best_single["wape"]) - float(fused_row["wape"])) / float(best_single["wape"])
    summary = output / "summary.md"
    lines = [
        "# Inventory Fusion backtest summary",
        "",
        f"- Holdout windows: {len(records)}",
        f"- Best single model: {best_single['model']} (WAPE {best_single['wape']:.4f})",
        f"- Adaptive fusion WAPE: {fused_row['wape']:.4f}",
        f"- Relative WAPE change vs best single: {lift:+.2%}",
        "- This inventory cost is a backtest proxy, not a production ROI claim.",
        "",
        "## Aggregate forecast metrics",
        "",
        _markdown_table(aggregate),
        "",
        "## Inventory proxy metrics",
        "",
        _markdown_table(inventory),
    ]
    summary.write_text("\n".join(lines), encoding="utf-8")
    return {
        "metrics": metrics_path,
        "weights": weights_path,
        "inventory": inventory_path,
        "comparison": comparison_path,
        "evidence": evidence_path,
        "weights_plot": weights_plot_path,
        "summary": summary,
    }


def _markdown_table(frame: pd.DataFrame) -> str:
    columns = list(frame.columns)
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for _, row in frame.iterrows():
        values = []
        for column in columns:
            value = row[column]
            values.append(f"{value:.4f}" if isinstance(value, (float, np.floating)) else str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)

