"""
LLaMA HREDD Adverse Text DistilBERT ONNX Adapter
-----------------------------------------------
Loads the adverse text classifier from `llama-hredd-adverse-text-distilbert-onnx`.
Predicts 16 adverse human rights and environmental risk categories:
- biodiversity_loss
- child_labour
- deforestation
- discrimination
- fatal_incident
- forced_labour
- freedom_of_association
- gbvh (gender-based violence and harassment)
- hazardous_waste
- none
- osh_nonfatal (occupational safety & health)
- retaliation
- toxic_pollution
- trafficking
- wage_theft
- water_depletion
"""
from __future__ import annotations
import json
import logging
from threading import Lock
from typing import Dict, Any, List, Optional
import numpy as np

from app.supply_chain_ai.config import HREDD_MODEL_PATH

logger = logging.getLogger("powerhouse.supply_chain_ai.hredd")


class HreddRiskAdapter:
    _instance: Optional["HreddRiskAdapter"] = None
    _lock = Lock()

    def __init__(self) -> None:
        self._session = None
        self._tokenizer = None
        self._label_map: List[str] = []
        self._is_loaded = False
        self._load_lock = Lock()

    @classmethod
    def get(cls) -> "HreddRiskAdapter":
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
                import onnxruntime as ort
                from transformers import AutoTokenizer

                onnx_file = HREDD_MODEL_PATH / "onnx" / "model_quantized.onnx"
                label_map_file = HREDD_MODEL_PATH / "label_map.json"

                if not onnx_file.exists() or not label_map_file.exists():
                    logger.warning(f"HREDD model or label map not found at {HREDD_MODEL_PATH}")
                    return False

                with open(label_map_file, "r", encoding="utf-8") as f:
                    self._label_map = json.load(f)

                self._tokenizer = AutoTokenizer.from_pretrained(str(HREDD_MODEL_PATH))
                self._session = ort.InferenceSession(
                    str(onnx_file),
                    providers=["CPUExecutionProvider"]
                )
                self._is_loaded = True
                logger.info("HREDD ONNX model loaded successfully with 16 adverse categories")
                return True
            except Exception as e:
                logger.error(f"Failed to load HREDD ONNX model: {e}", exc_info=True)
                return False

    def predict_adverse_signals(self, text: str) -> Dict[str, Any]:
        """Run ONNX model and return adverse category probabilities."""
        if not self._ensure_loaded():
            return self._heuristic_fallback(text)

        try:
            enc = self._tokenizer(
                text,
                return_tensors="np",
                truncation=True,
                max_length=256,
                padding=True
            )
            input_names = [inp.name for inp in self._session.get_inputs()]
            inputs = {k: v for k, v in enc.items() if k in input_names}

            logits = self._session.run(None, inputs)[0][0]
            # Sigmoid for multi-label classification
            scores = 1.0 / (1.0 + np.exp(-logits))

            category_scores = {}
            for idx, label in enumerate(self._label_map):
                category_scores[label] = round(float(scores[idx]), 4)

            # Sort top adverse categories (excluding "none")
            adverse_candidates = [
                (cat, sc) for cat, sc in category_scores.items() if cat != "none"
            ]
            adverse_candidates.sort(key=lambda x: x[1], reverse=True)

            top_signals = [
                {"category": cat, "score": sc, "risk_level": "CRITICAL" if sc > 0.65 else ("HIGH" if sc > 0.45 else "MEDIUM")}
                for cat, sc in adverse_candidates[:4]
                if sc > 0.25
            ]

            # Calculate composite ESG risk score (0-100)
            none_score = category_scores.get("none", 0.5)
            max_adverse = adverse_candidates[0][1] if adverse_candidates else 0.0
            avg_top_adverse = float(np.mean([s[1] for s in adverse_candidates[:3]])) if adverse_candidates else 0.0

            esg_risk_score = round(min(100.0, max(0.0, (avg_top_adverse * 0.7 + max_adverse * 0.3) * 100)), 1)
            # ESG Health Score (100 = clean, 0 = severe adverse)
            esg_health_score = round(max(0.0, 100.0 - esg_risk_score), 1)

            return {
                "esg_risk_score": esg_risk_score,
                "esg_health_score": esg_health_score,
                "top_adverse_signals": top_signals,
                "all_categories": category_scores,
                "model_source": "llama-hredd-adverse-text-distilbert-onnx (ONNX Runtime)",
            }
        except Exception as e:
            logger.error(f"HREDD ONNX inference error: {e}")
            return self._heuristic_fallback(text)

    def analyze_supplier_esg(
        self,
        supplier_name: str,
        country: str,
        audit_notes: str = "",
        news_reports: str = ""
    ) -> Dict[str, Any]:
        """Construct ESG text and evaluate supplier human rights and environmental compliance."""
        prompt = (
            f"Supplier Audit & News Evaluation: {supplier_name} located in {country}. "
            f"Audit findings: {audit_notes or 'Standard tier-1 supplier audit reports reviewed'}. "
            f"Media reports: {news_reports or 'No major public labor infractions flagged in recent quarter'}."
        )
        result = self.predict_adverse_signals(prompt)
        result["supplier_name"] = supplier_name
        result["country"] = country
        return result

    def _heuristic_fallback(self, text: str) -> Dict[str, Any]:
        lower = text.lower()
        signals = []
        risk_score = 18.0

        if "child" in lower or "forced" in lower or "traffick" in lower:
            signals.append({"category": "forced_labour", "score": 0.72, "risk_level": "CRITICAL"})
            risk_score = 78.0
        if "toxic" in lower or "waste" in lower or "pollution" in lower:
            signals.append({"category": "toxic_pollution", "score": 0.65, "risk_level": "HIGH"})
            risk_score = max(risk_score, 65.0)
        if "wage" in lower or "overtime" in lower or "strike" in lower:
            signals.append({"category": "wage_theft", "score": 0.58, "risk_level": "HIGH"})
            risk_score = max(risk_score, 55.0)

        return {
            "esg_risk_score": risk_score,
            "esg_health_score": round(100.0 - risk_score, 1),
            "top_adverse_signals": signals,
            "all_categories": {},
            "model_source": "hredd-fallback-heuristic",
        }
