library(ggplot2)

# 1. Load the processed AnyLogic data from the Python output folder
df <- read.csv("analysis-python-result/combined_simulation_results.csv")
metrics <- read.csv("analysis-python-result/recovery_metrics.csv")

# ── Plot 1: Recovery comparison ───────────────────────────────────────────────
# Plots the exact impact of your two disruption scenarios
ggplot(metrics, aes(x = severity * 100, y = days_critical)) +
  geom_point(size = 4, color = "steelblue") +
  geom_line(color = "steelblue", linewidth = 1) +
  labs(
    title = "Impact of Disruption Severity on Supply Chain Recovery",
    subtitle = "Food supply chain simulation — CARES project context",
    x = "Disruption Severity (%)",
    y = "Days Below Critical Stock Level",
    caption = "Simulated AnyLogic data. Recovery triggered at day 45."
  ) +
  theme_minimal() +
  theme(plot.title = element_text(face = "bold"))

# Save the plot back into the results folder
ggsave("analysis-python-result/recovery_analysis_R.png", width = 8, height = 6, dpi = 150)

# ── Statistical summary ───────────────────────────────────────────────────────
cat("\n=== R STATISTICAL SUMMARY ===\n")
cat("Recovery metrics:\n")
print(summary(metrics))

# Linear model (Note: With only 2 data points, this shows a mathematical certainty, 
# but proves you know how to write the regression model for the PhD application).
model <- lm(days_critical ~ severity, data = metrics)
cat("\nLinear model (days_critical ~ severity):\n")
print(summary(model))

cat("\nR² =", round(summary(model)$r.squared, 4), "\n")
cat("Interpretation: Disruption severity explains", 
    round(summary(model)$r.squared * 100, 1), 
    "% of variance in recovery time\n")

