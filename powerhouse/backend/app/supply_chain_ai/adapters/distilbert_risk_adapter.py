"""
Supply Chain DistilBERT Risk Classifier Adapter
-----------------------------------------------
Loads the fine-tuned DistilBERT model from `supply-chain-distilbert-risk`.
Performs 4-class risk classification: LOW | MEDIUM | HIGH | CRITICAL.
"""
from __future__ import annotations
import logging
from threading import Lock
from typing import Dict, Any, List, Optional
import numpy as np

from app.supply_chain_ai.config import DISTILBERT_RISK_PATH, get_effective_device

logger = logging.getLogger("powerhouse.supply_chain_ai.distilbert")

RISK_LABELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class DistilBertRiskAdapter:
    _instance: Optional["DistilBertRiskAdapter"] = None
    _lock = Lock()

    def __init__(self) -> None:
        self._model = None
        self._tokenizer = None
        self._device = None
        self._is_loaded = False
        self._load_lock = Lock()

    @classmethod
    def get(cls) -> "DistilBertRiskAdapter":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def _ensure_loaded(self) -> bool:
        if self._is_loaded:
            return True
        with self._load_lock:
            if self._is_loaded:
                return True
            try:
                import torch
                from transformers import AutoTokenizer, AutoModelForSequenceClassification

                if not DISTILBERT_RISK_PATH.exists() or not (DISTILBERT_RISK_PATH / "model.safetensors").exists():
                    logger.warning(f"DistilBERT risk model not found at {DISTILBERT_RISK_PATH}")
                    return False

                logger.info(f"Loading Supply Chain DistilBERT model from {DISTILBERT_RISK_PATH}...")
                self._tokenizer = AutoTokenizer.from_pretrained(str(DISTILBERT_RISK_PATH))
                self._model = AutoModelForSequenceClassification.from_pretrained(str(DISTILBERT_RISK_PATH))

                dev_str = get_effective_device()
                self._device = torch.device(dev_str if torch.cuda.is_available() and dev_str == "cuda" else "cpu")
                self._model = self._model.to(self._device)
                self._model.eval()
                self._is_loaded = True
                logger.info(f"DistilBERT risk model successfully loaded on {self._device}")
                return True
            except Exception as e:
                logger.error(f"Failed to load DistilBERT risk model: {e}", exc_info=True)
                return False

    def classify_text(self, text: str) -> Dict[str, Any]:
        """Classify raw text description into LOW/MEDIUM/HIGH/CRITICAL."""
        if not self._ensure_loaded():
            return self._heuristic_fallback(text)

        try:
            import torch
            inputs = self._tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=256,
                padding=True
            )
            inputs = {k: v.to(self._device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self._model(**inputs)
                logits = outputs.logits.squeeze(0).cpu().numpy()

            # Softmax
            exp_logits = np.exp(logits - np.max(logits))
            probs = (exp_logits / np.sum(exp_logits)).tolist()

            pred_idx = int(np.argmax(probs))
            predicted_label = RISK_LABELS[pred_idx]
            confidence = float(probs[pred_idx])

            return {
                "predicted_risk": predicted_label,
                "risk_level": predicted_label,
                "confidence": round(confidence, 4),
                "probabilities": {
                    RISK_LABELS[i]: round(float(probs[i]), 4)
                    for i in range(len(RISK_LABELS))
                },
                "model_source": "supply-chain-distilbert-risk (local PyTorch)",
                "raw_logits": [round(float(x), 4) for x in logits.tolist()],
            }
        except Exception as e:
            logger.error(f"DistilBERT inference error: {e}")
            return self._heuristic_fallback(text)

    def analyze_supplier(
        self,
        name: str,
        region: str,
        products: List[str],
        lead_time_days: int,
        dependency_pct: float,
        single_source: bool = False,
        recent_delivery_delays: int = 0,
        unverified_compliance: bool = False,
    ) -> Dict[str, Any]:
        """Construct structured prompt text and evaluate supplier risk."""
        text = (
            f"Supplier: {name}. Region: {region}. Product: {', '.join(products) if products else 'General Component'}. "
            f"Lead Time: {lead_time_days} days. Dependency: {dependency_pct}%. "
            f"Single Source Dependency: {'Yes' if single_source else 'No'}. "
            f"Recent Delays: {recent_delivery_delays} instances. "
            f"Compliance Status: {'Unverified Documents' if unverified_compliance else 'Verified'}. "
        )
        if single_source and dependency_pct > 75:
            text += "Critical sole-source vulnerability with zero alternate qualified vendors in corridor."
        if lead_time_days > 25:
            text += "Severe long-haul shipping transit with port congestion exposure."

        result = self.classify_text(text)
        result["supplier_name"] = name
        result["region"] = region
        result["lead_time_days"] = lead_time_days
        result["evaluated_prompt"] = text
        return result

    def _heuristic_fallback(self, text: str) -> Dict[str, Any]:
        lower = text.lower()
        if "critical" in lower or "sole-source" in lower or "outage" in lower or "closure" in lower:
            probs = {"LOW": 0.05, "MEDIUM": 0.10, "HIGH": 0.25, "CRITICAL": 0.60}
            pred = "CRITICAL"
        elif "high" in lower or "delay" in lower or "congestion" in lower:
            probs = {"LOW": 0.10, "MEDIUM": 0.20, "HIGH": 0.55, "CRITICAL": 0.15}
            pred = "HIGH"
        elif "warning" in lower or "moderate" in lower:
            probs = {"LOW": 0.20, "MEDIUM": 0.55, "HIGH": 0.20, "CRITICAL": 0.05}
            pred = "MEDIUM"
        else:
            probs = {"LOW": 0.70, "MEDIUM": 0.20, "HIGH": 0.08, "CRITICAL": 0.02}
            pred = "LOW"

        return {
            "predicted_risk": pred,
            "risk_level": pred,
            "confidence": probs[pred],
            "probabilities": probs,
            "model_source": "distilbert-fallback-heuristic",
            "raw_logits": [],
        }
