import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# ── Simulate AnyLogic output (replace with real CSV if you have it) ──────────
np.random.seed(42)
time_steps = np.arange(0, 100, 1)

def simulate_stock(disruption_severity, recovery_time=45):
    """Simulate warehouse stock level over time given disruption severity"""
    stock = []
    level = 450  # initial stock
    
    for t in time_steps:
        if t < 30:
            level += np.random.normal(20, 5)   # normal inflow
        elif t < recovery_time:
            # Disruption phase: reduced inflow
            level += np.random.normal(20 * (1 - disruption_severity), 5) - 25
        else:
            # Recovery phase: backup supplier
            level += np.random.normal(30, 5) - 25
        
        level = max(0, level)  # stock can't go negative
        stock.append(level)
    
    return stock

# ── Run 4 severity scenarios ─────────────────────────────────────────────────
severities = [0.2, 0.4, 0.6, 0.8]
results = {}

for s in severities:
    results[f"severity_{s}"] = simulate_stock(s)

df = pd.DataFrame(results, index=time_steps)
df.index.name = "time"

# ── ANALYSIS 1: Time-series plot ─────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("Food Supply Chain Resilience Under Climate Disruption", 
             fontsize=14, fontweight='bold')

for i, (col, ax) in enumerate(zip(df.columns, axes.flatten())):
    severity = severities[i]
    ax.plot(df.index, df[col], color='steelblue', linewidth=2)
    ax.axvline(x=30, color='red', linestyle='--', alpha=0.7, label='Disruption')
    ax.axvline(x=45, color='green', linestyle='--', alpha=0.7, label='Recovery')
    ax.axhline(y=100, color='orange', linestyle=':', alpha=0.7, label='Critical level')
    ax.set_title(f"Disruption Severity: {severity*100:.0f}%")
    ax.set_xlabel("Time (days)")
    ax.set_ylabel("Stock Level (units)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("disruption_scenarios.png", dpi=150, bbox_inches='tight')
plt.show()
print("Plot saved: disruption_scenarios.png")

# ── ANALYSIS 2: Recovery metrics ─────────────────────────────────────────────
print("\n=== RECOVERY METRICS ===")
print(f"{'Severity':>12} | {'Min Stock':>10} | {'Days Critical':>14} | {'Recovery Time':>14}")
print("-" * 60)

metrics = []
for s in severities:
    col = f"severity_{s}"
    stock = df[col].values
    
    min_stock = stock.min()
    days_critical = (stock < 100).sum()  # days below critical threshold
    
    # Recovery time: first time stock > 200 after disruption
    post_disruption = stock[45:]
    recovery_idx = np.where(post_disruption > 200)[0]
    recovery_time = recovery_idx[0] if len(recovery_idx) > 0 else 99
    
    metrics.append({
        "severity": s,
        "min_stock": min_stock,
        "days_critical": days_critical,
        "recovery_time": recovery_time
    })
    
    print(f"{s*100:>11.0f}% | {min_stock:>10.1f} | {days_critical:>14d} | {recovery_time:>14d}")

metrics_df = pd.DataFrame(metrics)

# ── ANALYSIS 3: Correlation analysis ─────────────────────────────────────────
print("\n=== STATISTICAL ANALYSIS ===")

# Kruskal-Wallis test (same method as energy paper!)
# Tests whether disruption severity significantly affects stock levels
groups = [df[f"severity_{s}"].values for s in severities]
stat, p_value = stats.kruskal(*groups)
print(f"Kruskal-Wallis test: H={stat:.4f}, p={p_value:.6f}")
print(f"Result: {'Significant difference' if p_value < 0.05 else 'No significant difference'} "
      f"across severity levels (α=0.05)")

# Pearson correlation: severity vs days_critical
corr, p_corr = stats.pearsonr(
    metrics_df["severity"], 
    metrics_df["days_critical"]
)
print(f"\nCorrelation (severity vs days_critical): r={corr:.4f}, p={p_corr:.4f}")
print(f"Interpretation: {'Strong' if abs(corr) > 0.7 else 'Moderate'} "
      f"{'positive' if corr > 0 else 'negative'} relationship")

# ── ANALYSIS 4: Optimization — minimum backup supplier rate needed ────────────
print("\n=== OPTIMIZATION ANALYSIS ===")
print("Minimum backup supplier rate to prevent stock-out by severity:")

for s in severities:
    # Simple calculation: how much backup supply is needed to keep stock > 0
    deficit_rate = 25 * s          # daily deficit during disruption
    min_backup = max(0, deficit_rate - 20 * (1 - s))
    print(f"  Severity {s*100:.0f}%: minimum backup rate = {min_backup:.1f} units/day")

# ── Save all results ──────────────────────────────────────────────────────────
df.to_csv("simulation_results.csv")
metrics_df.to_csv("recovery_metrics.csv", index=False)
print("\nResults saved to CSV files.")