# Supply Chain Disruption Analysis in R
# Complements the Python simulation

library(ggplot2)

# Load simulation results
df <- read.csv("simulation_results.csv")
metrics <- read.csv("recovery_metrics.csv")

# ── Plot 1: Recovery comparison ───────────────────────────────────────────────
ggplot(metrics, aes(x = severity * 100, y = days_critical)) +
  geom_point(size = 4, color = "steelblue") +
  geom_line(color = "steelblue", linewidth = 1) +
  geom_smooth(method = "lm", se = TRUE, color = "red", linetype = "dashed") +
  labs(
    title = "Impact of Disruption Severity on Supply Chain Recovery",
    subtitle = "Food supply chain simulation — CARES project context",
    x = "Disruption Severity (%)",
    y = "Days Below Critical Stock Level",
    caption = "Simulated data. Recovery triggered at day 45."
  ) +
  theme_minimal() +
  theme(plot.title = element_text(face = "bold"))

ggsave("recovery_analysis.png", width = 8, height = 6, dpi = 150)

# ── Statistical summary ───────────────────────────────────────────────────────
cat("\n=== R STATISTICAL SUMMARY ===\n")
cat("Recovery metrics:\n")
print(summary(metrics))

# Linear model: severity predicts days_critical
model <- lm(days_critical ~ severity, data = metrics)
cat("\nLinear model (days_critical ~ severity):\n")
print(summary(model))

cat("\nR² =", round(summary(model)$r.squared, 4), "\n")
cat("Interpretation: Disruption severity explains", 
    round(summary(model)$r.squared * 100, 1), 
    "% of variance in recovery time\n")