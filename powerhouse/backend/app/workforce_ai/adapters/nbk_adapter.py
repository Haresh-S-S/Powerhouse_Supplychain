"""
NBK ATS Semantic Adapter
-------------------------
Wraps `nbk-ats-semantic-v1-en` — a fine-tuned sentence transformer for
resume ↔ job-description semantic matching (8,192-token context window).

Provides:
  • Cosine similarity between resume text and job description
  • Ensemble ATS score (Ridge + Neural MLP score mapper) if weights present
  • Role matching and ranking across multiple job descriptions

See model README for the ensemble weight format (ridge_weights.json,
neural_weights.json, poly_features.json — stored in the model folder).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger("[WORKFORCE AI]")


class NBKAdapter:
    """
    Singleton adapter for NBK ATS Semantic v1 model.
    Lazy-loads model + ensemble weights on first use.
    """

    _instance: Optional["NBKAdapter"] = None
    _lock = Lock()

    def __init__(self) -> None:
        self._model = None
        self._score_mapper = None      # Ridge regression
        self._neural_mapper = None     # MLP regressor
        self._poly_features = None
        self._available: Optional[bool] = None
        self._load_lock = Lock()

    @classmethod
    def get(cls) -> "NBKAdapter":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def _load_ensemble_weights(self, model_dir: Path) -> bool:
        """Load Ridge + Neural + Poly weights from JSON files in the model dir."""
        try:
            from sklearn.linear_model import Ridge
            from sklearn.neural_network import MLPRegressor
            from sklearn.preprocessing import PolynomialFeatures

            ridge_path = model_dir / "ridge_weights.json"
            neural_path = model_dir / "neural_weights.json"
            poly_path = model_dir / "poly_features.json"

            if not (ridge_path.exists() and neural_path.exists() and poly_path.exists()):
                logger.warning(
                    "[WORKFORCE AI] NBK ensemble weight files not found – "
                    "raw cosine similarity will be used."
                )
                return False

            with open(ridge_path) as f:
                ridge_data = json.load(f)
            with open(neural_path) as f:
                neural_data = json.load(f)
            with open(poly_path) as f:
                poly_data = json.load(f)

            # Reconstruct Ridge
            score_mapper = Ridge(alpha=ridge_data["alpha"])
            score_mapper.coef_ = np.array(ridge_data["coefficients"])
            score_mapper.intercept_ = ridge_data["intercept"]
            score_mapper.n_features_in_ = ridge_data["n_features_in"]

            # Reconstruct Neural MLP
            neural_mapper = MLPRegressor(
                hidden_layer_sizes=tuple(neural_data["hidden_layer_sizes"]),
                activation=neural_data["activation"],
            )
            neural_mapper.coefs_ = [np.array(c) for c in neural_data["coefs"]]
            neural_mapper.intercepts_ = [np.array(i) for i in neural_data["intercepts"]]
            neural_mapper.n_features_in_ = neural_data["n_features_in"]

            # Reconstruct PolynomialFeatures
            poly_features = PolynomialFeatures(
                degree=poly_data["degree"],
                include_bias=poly_data["include_bias"],
            )
            poly_features.n_features_in_ = poly_data["n_features_in"]
            poly_features.n_output_features_ = poly_data["n_output_features"]

            self._score_mapper = score_mapper
            self._neural_mapper = neural_mapper
            self._poly_features = poly_features
            logger.info("[WORKFORCE AI] NBK ensemble weights loaded")
            return True

        except ImportError:
            logger.warning("[WORKFORCE AI] scikit-learn missing – ensemble weights skipped")
            return False
        except Exception as e:
            logger.warning(f"[WORKFORCE AI] NBK ensemble load error: {e}")
            return False

    def _try_load(self) -> bool:
        from app.workforce_ai.config import NBK_ATS_MODEL_PATH

        model_path = Path(NBK_ATS_MODEL_PATH)
        if not model_path.exists():
            logger.warning(f"[WORKFORCE AI] NBK model path not found: {model_path}")
            return False

        try:
            from sentence_transformers import SentenceTransformer  # noqa
            logger.info(f"[WORKFORCE AI] Loading NBK ATS model from {model_path} …")
            self._model = SentenceTransformer(str(model_path))
            logger.info("[WORKFORCE AI] NBK ATS model loaded")
            self._load_ensemble_weights(model_path)
            return True
        except ImportError:
            logger.warning(
                "[WORKFORCE AI] `sentence-transformers` not installed – "
                "role matching unavailable."
            )
            return False
        except Exception as e:
            logger.error(f"[WORKFORCE AI] NBK load failed: {e}")
            return False

    def _ensure_loaded(self) -> bool:
        if self._available is None:
            with self._load_lock:
                if self._available is None:
                    self._available = self._try_load()
        return self._available

    # ──────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────

    def _raw_cosine(self, emb_a, emb_b) -> float:
        dot = float(np.dot(emb_a, emb_b))
        norm = float(np.linalg.norm(emb_a) * np.linalg.norm(emb_b))
        return float(dot / norm) if norm > 0 else 0.0

    def _predict_ats_score(self, similarity: float) -> float:
        """Map raw cosine → ATS score (0-100) using ensemble if available."""
        if (
            self._score_mapper is not None
            and self._neural_mapper is not None
            and self._poly_features is not None
        ):
            try:
                features = self._poly_features.transform([[similarity]])
                ridge_pred = self._score_mapper.predict(features)[0]
                neural_pred = self._neural_mapper.predict(features)[0]
                score = float(ridge_pred * 0.5 + neural_pred * 0.5)
                return float(np.clip(score, 0, 100))
            except Exception as e:
                logger.warning(f"[WORKFORCE AI] Ensemble scoring failed: {e}")
        # Fallback: linear scale
        return round(similarity * 100, 1)

    def match_resume_to_role(
        self,
        resume_text: str,
        role_description: str,
        role_name: str = "Target Role",
    ) -> Dict[str, Any]:
        """
        Compute semantic similarity between a resume and a job description.
        Returns a structured match result.
        """
        if not self._ensure_loaded():
            return _unavailable_match(role_name)

        try:
            resume_emb = self._model.encode(resume_text)
            role_emb = self._model.encode(role_description)
            cosine = self._raw_cosine(resume_emb, role_emb)
            ats_score = self._predict_ats_score(cosine)

            fit_label = _fit_label(ats_score)

            return {
                "role_name": role_name,
                "ats_score": round(ats_score, 1),
                "semantic_similarity": round(cosine, 3),
                "fit_label": fit_label,
                "match_explanation": _match_explanation(ats_score, role_name),
                "ai_available": True,
            }
        except Exception as e:
            logger.error(f"[WORKFORCE AI] NBK match error: {e}")
            return _unavailable_match(role_name)

    def rank_roles(
        self,
        resume_text: str,
        roles: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Rank a list of roles by semantic match to a resume.
        Each role dict must have 'role_name' and optionally 'description'.
        """
        if not self._ensure_loaded():
            return [_unavailable_match(r.get("role_name", "Unknown")) for r in roles]

        try:
            resume_emb = self._model.encode(resume_text)
            results = []
            for role in roles:
                role_name = role.get("role_name", "Unknown")
                desc = role.get("description") or role_name
                role_emb = self._model.encode(desc)
                cosine = self._raw_cosine(resume_emb, role_emb)
                ats_score = self._predict_ats_score(cosine)
                results.append({
                    "role_name": role_name,
                    "ats_score": round(ats_score, 1),
                    "semantic_similarity": round(cosine, 3),
                    "fit_label": _fit_label(ats_score),
                    "match_explanation": _match_explanation(ats_score, role_name),
                    "ai_available": True,
                })
            results.sort(key=lambda x: x["ats_score"], reverse=True)
            return results
        except Exception as e:
            logger.error(f"[WORKFORCE AI] NBK rank_roles error: {e}")
            return [_unavailable_match(r.get("role_name", "Unknown")) for r in roles]


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _fit_label(score: float) -> str:
    if score >= 80:
        return "Strong Potential Fit"
    elif score >= 65:
        return "Moderate Potential Fit"
    elif score >= 50:
        return "Development Opportunity"
    else:
        return "Limited Alignment"


def _match_explanation(score: float, role_name: str) -> str:
    if score >= 80:
        return (
            f"Strong semantic alignment detected between the employee profile and "
            f"the {role_name} requirements. Significant skill overlap observed."
        )
    elif score >= 65:
        return (
            f"Moderate alignment with {role_name}. Several relevant skills match; "
            "targeted development in identified gap areas would strengthen fit."
        )
    elif score >= 50:
        return (
            f"Partial alignment with {role_name}. A structured development plan "
            "focusing on core required competencies is recommended."
        )
    else:
        return (
            f"Limited alignment with {role_name} at this time. This represents "
            "a significant development opportunity with a longer-term learning roadmap."
        )


def _unavailable_match(role_name: str) -> Dict[str, Any]:
    return {
        "role_name": role_name,
        "ats_score": None,
        "semantic_similarity": None,
        "fit_label": "AI Analysis Unavailable",
        "match_explanation": "Semantic matching model is currently unavailable.",
        "ai_available": False,
    }
