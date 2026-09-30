"""
Skill-Sim Adapter
------------------
Wraps the locally downloaded `alvperez/skill-sim-model` (SentenceTransformer,
all-mpnet-base-v2 fine-tuned on ESCO skill pairs) for:

  • Skill similarity scoring    – cosine distance in 768-D embedding space
  • Skill normalization         – nearest-neighbour canonical form lookup
  • Skill comparison            – employee skills vs role required skills
  • Skill-gap analysis          – returns matching, missing, and related skills

Threshold guidance from README: ≥0.65 = "definitely related"; tune as needed.
"""
from __future__ import annotations

import logging
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("[WORKFORCE AI]")

_RELATED_THRESHOLD = 0.55   # configurable via SKILL_SIM_THRESHOLD env-var
_MATCH_THRESHOLD = 0.70     # considered a match


class SkillSimAdapter:
    """
    Singleton adapter for skill-sim-model.
    Lazy-loads the SentenceTransformer on first use.
    """

    _instance: Optional["SkillSimAdapter"] = None
    _lock = Lock()

    def __init__(self) -> None:
        self._model = None
        self._available: Optional[bool] = None
        self._load_lock = Lock()

    @classmethod
    def get(cls) -> "SkillSimAdapter":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def _try_load(self) -> bool:
        from app.workforce_ai.config import SKILL_SIM_MODEL_PATH

        model_path = Path(SKILL_SIM_MODEL_PATH)
        if not model_path.exists():
            logger.warning(
                f"[WORKFORCE AI] Skill-Sim model path not found: {model_path}"
            )
            return False

        try:
            from sentence_transformers import SentenceTransformer  # noqa
            logger.info(f"[WORKFORCE AI] Loading Skill-Sim from {model_path} …")
            self._model = SentenceTransformer(str(model_path))
            logger.info("[WORKFORCE AI] Skill-Sim loaded")
            return True
        except ImportError:
            logger.warning(
                "[WORKFORCE AI] `sentence-transformers` not installed. "
                "Skill similarity unavailable."
            )
            return False
        except Exception as e:
            logger.error(f"[WORKFORCE AI] Skill-Sim load failed: {e}")
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

    def encode(self, skills: List[str]):
        """Return embeddings tensor for a list of skill strings."""
        if not self._ensure_loaded():
            return None
        return self._model.encode(skills, convert_to_tensor=True, show_progress_bar=False)

    def similarity(self, skill_a: str, skill_b: str) -> float:
        """Return cosine similarity [0,1] between two skill phrases."""
        if not self._ensure_loaded():
            # Fallback: exact/substring match
            a, b = skill_a.lower().strip(), skill_b.lower().strip()
            if a == b:
                return 1.0
            if a in b or b in a:
                return 0.75
            return 0.0
        try:
            from sentence_transformers import util
            embs = self._model.encode([skill_a, skill_b], convert_to_tensor=True)
            score = util.pytorch_cos_sim(embs[0], embs[1]).item()
            return float(max(0.0, min(1.0, score)))
        except Exception as e:
            logger.error(f"[WORKFORCE AI] Skill-Sim similarity error: {e}")
            return 0.0

    def compare_skill_lists(
        self,
        employee_skills: List[str],
        required_skills: List[str],
    ) -> Dict[str, Any]:
        """
        Compare employee skills against required role skills.
        Returns:
            matching_skills   – employee skills that satisfy a requirement (score ≥ MATCH)
            missing_skills    – required skills the employee doesn't cover
            related_skills    – employee skills semantically close but not a direct match
            coverage_percent  – rough % of requirements satisfied
            skill_pairs       – detailed pairwise scores
        """
        from app.workforce_ai.config import SKILL_SIM_THRESHOLD

        related_thr = SKILL_SIM_THRESHOLD
        match_thr = _MATCH_THRESHOLD

        if not employee_skills or not required_skills:
            return {
                "matching_skills": [],
                "missing_skills": required_skills,
                "related_skills": [],
                "coverage_percent": 0,
                "skill_pairs": [],
                "ai_available": self._available or False,
            }

        if not self._ensure_loaded():
            # String-based fallback
            return _string_compare(employee_skills, required_skills)

        try:
            from sentence_transformers import util
            import torch

            emp_embs = self._model.encode(employee_skills, convert_to_tensor=True)
            req_embs = self._model.encode(required_skills, convert_to_tensor=True)

            # (num_req × num_emp) cosine similarity matrix
            sim_matrix = util.pytorch_cos_sim(req_embs, emp_embs)

            matching_skills: List[str] = []
            missing_skills: List[str] = []
            related_skills: List[str] = []
            skill_pairs: List[Dict] = []

            for req_idx, req_skill in enumerate(required_skills):
                row = sim_matrix[req_idx]
                best_score, best_emp_idx = torch.max(row, dim=0)
                score = float(best_score)
                best_emp_skill = employee_skills[int(best_emp_idx)]

                skill_pairs.append(
                    {
                        "required": req_skill,
                        "best_match": best_emp_skill,
                        "score": round(score, 3),
                        "status": (
                            "match"
                            if score >= match_thr
                            else ("related" if score >= related_thr else "missing")
                        ),
                    }
                )

                if score >= match_thr:
                    matching_skills.append(req_skill)
                elif score >= related_thr:
                    related_skills.append(req_skill)
                    missing_skills.append(req_skill)
                else:
                    missing_skills.append(req_skill)

            total = len(required_skills)
            coverage = int(round(len(matching_skills) / total * 100)) if total else 0

            return {
                "matching_skills": matching_skills,
                "missing_skills": missing_skills,
                "related_skills": related_skills,
                "coverage_percent": coverage,
                "skill_pairs": skill_pairs,
                "ai_available": True,
            }

        except Exception as e:
            logger.error(f"[WORKFORCE AI] Skill-Sim compare error: {e}")
            return _string_compare(employee_skills, required_skills)

    def find_similar_skills(
        self, query_skill: str, candidate_skills: List[str], top_n: int = 5
    ) -> List[Tuple[str, float]]:
        """Return top-N most similar skills from candidates."""
        if not self._ensure_loaded() or not candidate_skills:
            return []
        try:
            from sentence_transformers import util
            query_emb = self._model.encode([query_skill], convert_to_tensor=True)
            cand_embs = self._model.encode(candidate_skills, convert_to_tensor=True)
            scores = util.pytorch_cos_sim(query_emb, cand_embs)[0].tolist()
            ranked = sorted(
                zip(candidate_skills, scores), key=lambda x: x[1], reverse=True
            )
            return [(sk, round(sc, 3)) for sk, sc in ranked[:top_n]]
        except Exception as e:
            logger.error(f"[WORKFORCE AI] Skill-Sim find_similar error: {e}")
            return []


# ──────────────────────────────────────────────────────────────────────────────
# String-based fallback (no model)
# ──────────────────────────────────────────────────────────────────────────────

def _string_compare(
    employee_skills: List[str], required_skills: List[str]
) -> Dict[str, Any]:
    emp_lower = [s.lower().strip() for s in employee_skills]
    matching, missing, pairs = [], [], []
    for req in required_skills:
        req_l = req.lower().strip()
        is_match = any(req_l == e or req_l in e or e in req_l for e in emp_lower)
        if is_match:
            matching.append(req)
            pairs.append({"required": req, "best_match": req, "score": 1.0, "status": "match"})
        else:
            missing.append(req)
            pairs.append({"required": req, "best_match": None, "score": 0.0, "status": "missing"})

    total = len(required_skills)
    coverage = int(round(len(matching) / total * 100)) if total else 0
    return {
        "matching_skills": matching,
        "missing_skills": missing,
        "related_skills": [],
        "coverage_percent": coverage,
        "skill_pairs": pairs,
        "ai_available": False,
    }
