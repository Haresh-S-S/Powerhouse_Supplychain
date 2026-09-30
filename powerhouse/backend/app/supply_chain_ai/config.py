"""
Supply Chain AI Configuration
-----------------------------
Centralized configuration and path discovery for all local AI assets:
- SupplyMind (disruption intelligence & scenario simulation)
- Inventory Fusion (demand forecasting & inventory optimization)
- Supply Chain DistilBERT Risk (supplier risk classification)
- LLaMA HREDD (adverse text human rights & ESG risk model - ONNX)
- Qwen3 (reasoning & natural language explanations)
- smolagents (agent orchestration & tool calling)
- OR-Tools (vehicle routing & route optimization)
"""
import os
import logging
from pathlib import Path

logger = logging.getLogger("powerhouse.supply_chain_ai")

# Workspace root is two levels up from backend/app
WORKSPACE_ROOT = Path("d:/WorkForcePowerHouseSAP")
BACKEND_ROOT = Path("d:/WorkForcePowerHouseSAP/powerhouse/backend")

# Master toggle for Supply Chain AI features
SUPPLY_CHAIN_AI_ENABLED = os.getenv("SUPPLY_CHAIN_AI_ENABLED", "true").lower() in ("true", "1", "yes")

# Model & Repository paths
SUPPLYMIND_PATH = Path(os.getenv("SUPPLYMIND_PATH", str(WORKSPACE_ROOT / "Supplymind")))
INVENTORY_FUSION_PATH = Path(os.getenv("INVENTORY_FUSION_PATH", str(WORKSPACE_ROOT / "inventory-fusion-commercial-v1")))
DISTILBERT_RISK_PATH = Path(os.getenv("DISTILBERT_RISK_PATH", str(WORKSPACE_ROOT / "supply-chain-distilbert-risk")))
HREDD_MODEL_PATH = Path(os.getenv("HREDD_MODEL_PATH", str(WORKSPACE_ROOT / "llama-hredd-adverse-text-distilbert-onnx")))
CHRONOS_PATH = Path(os.getenv("CHRONOS_PATH", str(WORKSPACE_ROOT / "chronos-2")))
QWEN_MODEL_PATH = os.getenv("QWEN_MODEL_PATH", "")

# Device selection: auto, cuda, cpu
SUPPLY_CHAIN_DEVICE = os.getenv("SUPPLY_CHAIN_DEVICE", "auto")


def is_cuda_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


def get_effective_device() -> str:
    if SUPPLY_CHAIN_DEVICE == "cuda" and is_cuda_available():
        return "cuda"
    if SUPPLY_CHAIN_DEVICE == "auto":
        return "cuda" if is_cuda_available() else "cpu"
    return "cpu"


def check_ai_assets_status() -> dict:
    """Return status of all local AI assets."""
    return {
        "enabled": SUPPLY_CHAIN_AI_ENABLED,
        "device": get_effective_device(),
        "cuda_available": is_cuda_available(),
        "supplymind": {
            "path": str(SUPPLYMIND_PATH),
            "available": SUPPLYMIND_PATH.exists() and (SUPPLYMIND_PATH / "models.py").exists(),
        },
        "inventory_fusion": {
            "path": str(INVENTORY_FUSION_PATH),
            "available": INVENTORY_FUSION_PATH.exists() and (INVENTORY_FUSION_PATH / "src" / "inventory_fusion").exists(),
        },
        "distilbert_risk": {
            "path": str(DISTILBERT_RISK_PATH),
            "available": DISTILBERT_RISK_PATH.exists() and (DISTILBERT_RISK_PATH / "model.safetensors").exists(),
        },
        "hredd_risk": {
            "path": str(HREDD_MODEL_PATH),
            "available": HREDD_MODEL_PATH.exists() and (HREDD_MODEL_PATH / "onnx" / "model_quantized.onnx").exists(),
        },
        "qwen": {
            "path": QWEN_MODEL_PATH,
            "configured": bool(QWEN_MODEL_PATH and Path(QWEN_MODEL_PATH).exists()),
            "mode": "local_llm" if (QWEN_MODEL_PATH and Path(QWEN_MODEL_PATH).exists()) else "deterministic_expert_synthesizer",
        },
        "ortools": {
            "available": True,
        },
        "smolagents": {
            "available": True,
        },
    }
