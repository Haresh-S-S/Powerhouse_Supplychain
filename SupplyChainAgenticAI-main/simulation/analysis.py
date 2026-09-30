import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

print("Loading AnyLogic data...")
# ── 1. Load your actual AnyLogic data ──────────
try:
    df_normal = pd.read_csv('results/Normal_Disruption.csv')
    df_extreme = pd.read_csv('results/ExtremeDisruption.csv')
except FileNotFoundError:
    print("Error: Could not find the CSV files. Make sure you are running this from the 'simulation' folder.")
    exit()

# Combine into one DataFrame for analysis
df = pd.DataFrame()

# AnyLogic copy/paste usually puts the series name as the header.
# We map them to the column names the rest of the script expects.
# (Note: If you get a KeyError here, open your CSV in Excel and check the exact spelling of the column headers)
df['severity_0.2'] = df_normal['Warehouse Stock']
df['severity_0.8'] = df_extreme['Warehouse Stock']

# Grab the first column from the CSV to use as the Time index
time_col = df_normal.columns[0]
df.index = df_normal[time_col]
df.index.name = "time"

# We only have two scenarios now
severities = [0.2, 0.8]

# ── ANALYSIS 1: Time-series plot ─────────────────────────────────────────────
# Changed to 1 row, 2 columns to fit the two actual scenarios
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
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
print(f"{'Severity':>12} | {'Min Stock':>10} | {'Days Critical':>14}")
print("-" * 43)

metrics = []
for s in severities:
    col = f"severity_{s}"
    stock = df[col].values
    
    min_stock = stock.min()
    days_critical = (stock < 100).sum()  # days below critical threshold
    
    metrics.append({
        "severity": s,
        "min_stock": min_stock,
        "days_critical": days_critical
    })
    
    print(f"{s*100:>11.0f}% | {min_stock:>10.1f} | {days_critical:>14d}")

metrics_df = pd.DataFrame(metrics)

# ── ANALYSIS 3: Correlation analysis ─────────────────────────────────────────
print("\n=== STATISTICAL ANALYSIS ===")

# Kruskal-Wallis test 
groups = [df[f"severity_{s}"].dropna().values for s in severities]
stat, p_value = stats.kruskal(*groups)
print(f"Kruskal-Wallis test: H={stat:.4f}, p={p_value:.6f}")
print(f"Result: {'Significant difference' if p_value < 0.05 else 'No significant difference'} "
      f"across severity levels (α=0.05)")

# ── Save all results ──────────────────────────────────────────────────────────
output_folder = "analysis-python-result"

# This creates the folder if it does not already exist
os.makedirs(output_folder, exist_ok=True)

# Save the files directly into the new folder
df.to_csv(f"{output_folder}/combined_simulation_results.csv")
metrics_df.to_csv(f"{output_folder}/recovery_metrics.csv", index=False)

print(f"\nResults successfully saved to the '{output_folder}' folder.")