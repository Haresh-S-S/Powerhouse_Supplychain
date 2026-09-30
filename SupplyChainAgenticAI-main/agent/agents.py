from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from supply_data import generate_supply_chain_data, get_chain_summary

# ── State shared between agents ──────────────────────────────────────────────
class SupplyChainState(TypedDict):
    chain_status: str           # raw status text
    disruptions_found: List[str]  # list of critical nodes
    recommendations: List[str]  # replenishment actions
    final_report: str           # executive summary

# ── LLM (runs locally via Ollama, free) ─────────────────────────────────────
llm = OllamaLLM(model="llama3.2", temperature=0)

# ─────────────────────────────────────────────────────────────────────────────
# AGENT 1: Monitor Agent
# Reads supply chain data, identifies disruptions
# ─────────────────────────────────────────────────────────────────────────────
monitor_prompt = PromptTemplate.from_template("""
You are a supply chain monitoring agent for a food distribution network in Sweden.

Analyze this supply chain status and identify ALL nodes with CRITICAL or DISRUPTED status,
or nodes with less than 3 days of stock remaining.

Supply chain data:
{chain_status}

Respond with a numbered list of problem nodes and why each is critical.
Be brief and factual.
""")

def monitor_agent(state: SupplyChainState) -> SupplyChainState:
    print("\n[AGENT 1: Monitor] Scanning supply chain...")
    
    chain = monitor_prompt | llm
    result = chain.invoke({"chain_status": state["chain_status"]})
    
    # Extract disrupted nodes (simple parse)
    disruptions = []
    for line in state["chain_status"].split("\n"):
        if "CRITICAL" in line or "DISRUPTED" in line:
            node = line.split(":")[0].replace("- ", "").strip()
            disruptions.append(node)
    
    print(f"[AGENT 1] Found {len(disruptions)} disruptions: {disruptions}")
    print(f"[AGENT 1] Analysis:\n{result}")
    
    return {
        **state,
        "disruptions_found": disruptions
    }

# ─────────────────────────────────────────────────────────────────────────────
# AGENT 2: Replenishment Agent
# Decides what actions to take for each disrupted node
# ─────────────────────────────────────────────────────────────────────────────
replenishment_prompt = PromptTemplate.from_template("""
You are a supply chain replenishment agent for a food distribution network.

These nodes have been flagged as critical: {disruptions}

Full supply chain context:
{chain_status}

For each critical node, recommend ONE specific replenishment action.
Choose from: EMERGENCY_RESTOCK, REROUTE_FROM_SURPLUS, REDUCE_DEMAND, FIND_ALTERNATIVE_SUPPLIER

Format each recommendation as:
NODE: [node_name] | ACTION: [action] | REASON: [one sentence]
""")

def replenishment_agent(state: SupplyChainState) -> SupplyChainState:
    print("\n[AGENT 2: Replenishment] Generating recommendations...")
    
    if not state["disruptions_found"]:
        print("[AGENT 2] No disruptions to address.")
        return {**state, "recommendations": ["No action required - all nodes stable"]}
    
    chain = replenishment_prompt | llm
    result = chain.invoke({
        "disruptions": ", ".join(state["disruptions_found"]),
        "chain_status": state["chain_status"]
    })
    
    print(f"[AGENT 2] Recommendations:\n{result}")
    
    # Parse recommendations into list
    recommendations = [line.strip() for line in result.split("\n") 
                      if line.strip().startswith("NODE:")]
    
    return {
        **state,
        "recommendations": recommendations if recommendations else [result]
    }

# ─────────────────────────────────────────────────────────────────────────────
# AGENT 3: Report Agent
# Synthesizes findings into executive summary
# ─────────────────────────────────────────────────────────────────────────────
report_prompt = PromptTemplate.from_template("""
You are a supply chain analyst writing an executive summary for a food security manager.

Disruptions identified: {disruptions}

Recommended actions:
{recommendations}

Write a 3-sentence executive summary covering:
1. Current risk level (HIGH/MEDIUM/LOW)
2. Most urgent action needed
3. Expected outcome if actions are taken

Be concise and direct.
""")

def report_agent(state: SupplyChainState) -> SupplyChainState:
    print("\n[AGENT 3: Report] Generating executive summary...")
    
    chain = report_prompt | llm
    result = chain.invoke({
        "disruptions": ", ".join(state["disruptions_found"]) or "None",
        "recommendations": "\n".join(state["recommendations"])
    })
    
    print(f"[AGENT 3] Executive Summary:\n{result}")
    
    return {**state, "final_report": result}

# ─────────────────────────────────────────────────────────────────────────────
# BUILD THE GRAPH (LangGraph workflow)
# ─────────────────────────────────────────────────────────────────────────────
def build_supply_chain_graph():
    graph = StateGraph(SupplyChainState)
    
    # Add nodes (agents)
    graph.add_node("monitor", monitor_agent)
    graph.add_node("replenishment", replenishment_agent)
    graph.add_node("report", report_agent)
    
    # Define flow: monitor -> replenishment -> report -> END
    graph.set_entry_point("monitor")
    graph.add_edge("monitor", "replenishment")
    graph.add_edge("replenishment", "report")
    graph.add_edge("report", END)
    
    return graph.compile()