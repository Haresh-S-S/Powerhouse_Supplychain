from agents import build_supply_chain_graph, SupplyChainState
from supply_data import generate_supply_chain_data, get_chain_summary

def run_scenario(disruption: bool):
    scenario_name = "CLIMATE DISRUPTION SCENARIO" if disruption else "NORMAL OPERATIONS"
    print(f"\n{'='*60}")
    print(f"RUNNING: {scenario_name}")
    print('='*60)
    
    # Generate supply chain data
    df = generate_supply_chain_data(disruption=disruption)
    chain_status = get_chain_summary(df)
    
    # Build and run agent graph
    app = build_supply_chain_graph()
    
    initial_state = SupplyChainState(
        chain_status=chain_status,
        disruptions_found=[],
        recommendations=[],
        final_report=""
    )
    
    result = app.invoke(initial_state)
    
    print(f"\n{'='*60}")
    print("FINAL EXECUTIVE REPORT:")
    print('='*60)
    print(result["final_report"])
    
    return result

if __name__ == "__main__":
    # Scenario 1: Normal operations
    run_scenario(disruption=False)
    
    # Scenario 2: Climate disruption hits Farm_A
    run_scenario(disruption=True)