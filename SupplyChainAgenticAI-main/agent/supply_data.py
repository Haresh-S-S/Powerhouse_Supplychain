import pandas as pd
import random

def generate_supply_chain_data(disruption=False):
    """Simulate a 3-node food supply chain: Farm -> Warehouse -> Distribution"""
    
    data = {
        "node": ["Farm_A", "Farm_B", "Warehouse_Central", "Dist_Stockholm", "Dist_Gothenburg"],
        "stock_level": [850, 200, 450, 120, 380],   # units
        "daily_demand": [100, 100, 200, 80, 120],
        "days_of_stock": [8.5, 2.0, 2.25, 1.5, 3.17],
        "status": ["OK", "CRITICAL", "LOW", "CRITICAL", "OK"]
    }
    
    if disruption:
        # Simulate climate shock: Farm_A supply cut 60%
        data["stock_level"][0] = 340
        data["days_of_stock"][0] = 3.4
        data["status"][0] = "DISRUPTED"
    
    return pd.DataFrame(data)

def get_chain_summary(df):
    """Convert dataframe to text summary for the agent"""
    summary = "SUPPLY CHAIN STATUS REPORT:\n"
    for _, row in df.iterrows():
        summary += f"- {row['node']}: stock={row['stock_level']} units, "
        summary += f"days_remaining={row['days_of_stock']:.1f}, status={row['status']}\n"
    return summary

if __name__ == "__main__":
    print("=== Normal conditions ===")
    df = generate_supply_chain_data(disruption=False)
    print(get_chain_summary(df))
    
    print("\n=== After climate disruption ===")
    df_disrupted = generate_supply_chain_data(disruption=True)
    print(get_chain_summary(df_disrupted))