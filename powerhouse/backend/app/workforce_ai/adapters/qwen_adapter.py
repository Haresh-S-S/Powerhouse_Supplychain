"""
Qwen Adapter
------------
Wraps the Qwen3 local model for natural-language reasoning, explanations,
and career recommendations.

Since Qwen3-8B is a large model (typically 5-16 GB), this adapter:
  1. Checks whether a local Qwen model path is configured and available.
  2. If available: loads via `transformers` AutoModelForCausalLM (CPU or GPU).
  3. If NOT available (most development machines): uses a high-quality
     template-based reasoning engine that takes structured inputs from the
     other adapters and produces well-formatted recommendations.
     Template output is always clearly labeled as such so no fabrication occurs.

The template-based engine is NOT mock data – it reasons over the actual
skill-gap and role-match data provided by the other adapters.
"""
from __future__ import annotations

import logging
from threading import Lock
from typing import Any, Dict, List, Optional

logger = logging.getLogger("[WORKFORCE AI]")


class QwenAdapter:
    """
    Singleton adapter for Qwen3-8B local inference.
    Falls back to structured template reasoning when model is unavailable.
    """

    _instance: Optional["QwenAdapter"] = None
    _lock = Lock()

    def __init__(self) -> None:
        self._model = None
        self._tokenizer = None
        self._pipeline = None
        self._available: Optional[bool] = None
        self._load_lock = Lock()

    @classmethod
    def get(cls) -> "QwenAdapter":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def _try_load(self) -> bool:
        from app.workforce_ai.config import QWEN_MODEL_PATH, QWEN_AVAILABLE

        if not QWEN_AVAILABLE:
            logger.info(
                "[WORKFORCE AI] Qwen3 model path not configured or not found. "
                "Template-based reasoning will be used."
            )
            return False

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.bfloat16 if device == "cuda" else torch.float32

            logger.info(f"[WORKFORCE AI] Loading Qwen3 from {QWEN_MODEL_PATH} on {device} …")

            tokenizer = AutoTokenizer.from_pretrained(
                QWEN_MODEL_PATH, trust_remote_code=True
            )
            model = AutoModelForCausalLM.from_pretrained(
                QWEN_MODEL_PATH,
                torch_dtype=dtype,
                device_map="auto" if device == "cuda" else None,
                trust_remote_code=True,
            )
            if device == "cpu":
                model = model.to(device)

            self._pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=512,
                do_sample=False,
                device=0 if device == "cuda" else -1,
            )

            logger.info("[WORKFORCE AI] Qwen3 loaded")
            return True

        except ImportError as e:
            logger.warning(f"[WORKFORCE AI] Qwen requires `transformers` + `torch`: {e}")
            return False
        except Exception as e:
            logger.error(f"[WORKFORCE AI] Qwen load failed: {e}")
            return False

    def _ensure_loaded(self) -> bool:
        if self._available is None:
            with self._load_lock:
                if self._available is None:
                    self._available = self._try_load()
        return self._available

    # ──────────────────────────────────────────────────────────────────
    # Core generation
    # ──────────────────────────────────────────────────────────────────

    def _generate(self, prompt: str) -> str:
        """Run Qwen inference. Caller must ensure model is loaded."""
        try:
            result = self._pipeline(prompt)
            text = result[0]["generated_text"]
            # Strip the prompt prefix
            if text.startswith(prompt):
                text = text[len(prompt):].strip()
            return text
        except Exception as e:
            logger.error(f"[WORKFORCE AI] Qwen generation error: {e}")
            return ""

    # ──────────────────────────────────────────────────────────────────
    # Public API – each method tries Qwen first, falls back to templates
    # ──────────────────────────────────────────────────────────────────

    def generate_career_recommendation(
        self,
        employee_data: Dict[str, Any],
        skill_gap_data: Dict[str, Any],
        role_match_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a career development recommendation.
        Uses Qwen inference if available, otherwise template engine.
        """
        if self._ensure_loaded():
            return self._qwen_career_recommendation(
                employee_data, skill_gap_data, role_match_data
            )
        return _template_career_recommendation(
            employee_data, skill_gap_data, role_match_data
        )

    def generate_skill_gap_explanation(
        self,
        employee_data: Dict[str, Any],
        skill_gap_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Explain skill gaps in plain language."""
        if self._ensure_loaded():
            return self._qwen_skill_gap_explanation(employee_data, skill_gap_data)
        return _template_skill_gap_explanation(employee_data, skill_gap_data)

    def generate_development_plan(
        self,
        employee_data: Dict[str, Any],
        missing_skills: List[str],
        target_role: str,
    ) -> Dict[str, Any]:
        """Build a phased development plan."""
        if self._ensure_loaded():
            return self._qwen_development_plan(employee_data, missing_skills, target_role)
        return _template_development_plan(employee_data, missing_skills, target_role)

    def answer_workforce_question(
        self,
        question: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Answer a natural-language workforce question using available context."""
        if self._ensure_loaded():
            return self._qwen_answer(question, context)
        return _template_answer(question, context)

    def summarize_employee(
        self,
        employee_data: Dict[str, Any],
        skill_analysis: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Produce a professional capability summary for an employee."""
        if self._ensure_loaded():
            return self._qwen_summarize_employee(employee_data, skill_analysis)
        return _template_summarize_employee(employee_data, skill_analysis)

    # ──────────────────────────────────────────────────────────────────
    # Qwen-based implementations
    # ──────────────────────────────────────────────────────────────────

    def _qwen_career_recommendation(self, employee_data, skill_gap_data, role_match_data):
        current_role = employee_data.get("role", "Current Role")
        skills = ", ".join(employee_data.get("current_skills", [])[:15])
        missing = ", ".join(skill_gap_data.get("missing_skills", [])[:10])
        target = (role_match_data or {}).get("role_name", "Senior Role")
        prompt = (
            f"You are a professional career development advisor.\n\n"
            f"Employee current role: {current_role}\n"
            f"Current skills: {skills}\n"
            f"Target role: {target}\n"
            f"Skills gaps: {missing}\n\n"
            f"Provide a concise, structured career development recommendation with:\n"
            f"1. Current strengths (2-3 points)\n"
            f"2. Priority skills to develop (top 5)\n"
            f"3. Phased development roadmap (3 phases)\n"
            f"4. Recommended next role step\n\n"
            f"Be specific and practical."
        )
        text = self._generate(prompt)
        return {
            "source": "Qwen3-8B",
            "recommendation_text": text or "Unable to generate recommendation.",
            "ai_available": True,
        }

    def _qwen_skill_gap_explanation(self, employee_data, skill_gap_data):
        role = employee_data.get("role", "Current Role")
        missing = ", ".join(skill_gap_data.get("missing_skills", [])[:8])
        matching = ", ".join(skill_gap_data.get("matching_skills", [])[:8])
        prompt = (
            f"Explain the skill gaps for a {role} employee in plain language.\n"
            f"Matching skills: {matching}\n"
            f"Missing skills: {missing}\n\n"
            f"Provide a brief, encouraging explanation and the most important skill to learn first."
        )
        text = self._generate(prompt)
        return {"source": "Qwen3-8B", "explanation": text, "ai_available": True}

    def _qwen_development_plan(self, employee_data, missing_skills, target_role):
        current_role = employee_data.get("role", "Current Role")
        skills_str = ", ".join(missing_skills[:8])
        prompt = (
            f"Create a phased development plan for a {current_role} targeting {target_role}.\n"
            f"Skills to develop: {skills_str}\n\n"
            f"Structure as 3 clear phases with timeframes and milestones."
        )
        text = self._generate(prompt)
        return {
            "source": "Qwen3-8B",
            "plan_text": text,
            "target_role": target_role,
            "ai_available": True,
        }

    def _qwen_answer(self, question, context):
        ctx_str = str(context)[:2000]
        prompt = (
            f"You are a Workforce Intelligence assistant. Answer only based on the context provided.\n\n"
            f"Context: {ctx_str}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )
        text = self._generate(prompt)
        return {"source": "Qwen3-8B", "answer": text, "ai_available": True}

    def _qwen_summarize_employee(self, employee_data, skill_analysis):
        role = employee_data.get("role", "")
        dept = employee_data.get("department", "")
        exp = employee_data.get("experience_years", 0)
        skills = ", ".join(employee_data.get("current_skills", [])[:12])
        coverage = (skill_analysis or {}).get("coverage_percent", "N/A")
        prompt = (
            f"Summarize the professional profile of a {role} in the {dept} department "
            f"with {exp} years experience.\n"
            f"Skills: {skills}\n"
            f"Skill coverage against role requirements: {coverage}%\n\n"
            f"Write a 3-4 sentence professional summary suitable for a manager."
        )
        text = self._generate(prompt)
        return {"source": "Qwen3-8B", "summary": text, "ai_available": True}


# ══════════════════════════════════════════════════════════════════════════════
# Template-based reasoning engine (active when Qwen model is not available)
# All output is derived from real employee/gap/match data – no fabrication.
# ══════════════════════════════════════════════════════════════════════════════

def _template_career_recommendation(
    employee_data: Dict,
    skill_gap_data: Dict,
    role_match_data: Optional[Dict],
) -> Dict[str, Any]:
    current_role = employee_data.get("role", "Current Role")
    dept = employee_data.get("department", "Department")
    exp = employee_data.get("experience_years", 1)
    current_skills = employee_data.get("current_skills", [])
    matching = skill_gap_data.get("matching_skills", [])
    missing = skill_gap_data.get("missing_skills", [])
    related = skill_gap_data.get("related_skills", [])
    target_role = (role_match_data or {}).get("role_name", "Senior " + current_role)
    ats_score = (role_match_data or {}).get("ats_score")

    strengths = matching[:4] if matching else current_skills[:4]
    priority_skills = missing[:5]

    phases = _build_phases(priority_skills)

    score_note = f" (AI Role Match: {ats_score}%)" if ats_score else ""

    return {
        "source": "structured-analysis",
        "ai_available": False,
        "current_role": current_role,
        "target_role": target_role,
        "experience_years": exp,
        "current_strengths": strengths,
        "missing_skills": missing,
        "related_skills": related,
        "priority_skills": priority_skills,
        "ats_match_note": score_note,
        "development_phases": phases,
        "summary": (
            f"Based on skill analysis, {current_role} in {dept} shows strong alignment in "
            f"{', '.join(strengths[:3]) or 'core competencies'}. "
            f"To progress toward {target_role}{score_note}, focus on developing "
            f"{', '.join(priority_skills[:3]) or 'key technical skills'}."
        ),
    }


def _template_skill_gap_explanation(
    employee_data: Dict, skill_gap_data: Dict
) -> Dict[str, Any]:
    role = employee_data.get("role", "Current Role")
    matching = skill_gap_data.get("matching_skills", [])
    missing = skill_gap_data.get("missing_skills", [])
    related = skill_gap_data.get("related_skills", [])
    coverage = skill_gap_data.get("coverage_percent", 0)

    if not missing:
        explanation = (
            f"Excellent skill alignment for {role}. All required competencies are covered."
        )
    elif len(missing) <= 2:
        explanation = (
            f"Strong skill coverage at {coverage}% for {role}. "
            f"Minor gaps in {', '.join(missing)} can be addressed with focused short-term training."
        )
    else:
        top_missing = missing[:3]
        explanation = (
            f"Skill coverage for {role} is {coverage}%. "
            f"Strongest matching areas include {', '.join(matching[:3] or ['core competencies'])}. "
            f"Priority development areas: {', '.join(top_missing)}. "
            + (
                f"Related skills ({', '.join(related[:2])}) provide a solid foundation for faster learning."
                if related
                else "A structured learning pathway is recommended."
            )
        )

    return {
        "source": "structured-analysis",
        "ai_available": False,
        "explanation": explanation,
        "coverage_percent": coverage,
        "priority_skill": missing[0] if missing else None,
    }


def _template_development_plan(
    employee_data: Dict, missing_skills: List[str], target_role: str
) -> Dict[str, Any]:
    phases = _build_phases(missing_skills)
    current_role = employee_data.get("role", "Current Role")
    total_weeks = len(missing_skills) * 2 + 2

    return {
        "source": "structured-analysis",
        "ai_available": False,
        "current_role": current_role,
        "target_role": target_role,
        "estimated_weeks": total_weeks,
        "phases": phases,
        "summary": (
            f"Development plan from {current_role} → {target_role}: "
            f"{len(phases)} phases over approximately {total_weeks} weeks, "
            f"focusing on {', '.join(missing_skills[:3] or ['key competencies'])}."
        ),
    }


def _template_answer(question: str, context: Dict) -> Dict[str, Any]:
    q_lower = question.lower()
    employee = context.get("employee", {})
    skill_analysis = context.get("skill_analysis", {})
    role_match = context.get("role_match", {})

    current_skills = employee.get("current_skills", [])
    missing = skill_analysis.get("missing_skills", [])
    matching = skill_analysis.get("matching_skills", [])
    role_name = employee.get("role", "Current Role")
    coverage = skill_analysis.get("coverage_percent", 0)

    if any(k in q_lower for k in ["strongest", "strength", "best skill", "good at"]):
        answer = (
            f"Based on role requirement analysis, the strongest skills are: "
            f"{', '.join(matching[:5] or current_skills[:5] or ['No skills on record'])}. "
            f"Overall skill coverage is {coverage}%."
        )
    elif any(k in q_lower for k in ["missing", "gap", "need", "lacking"]):
        answer = (
            f"The identified skill gaps are: "
            f"{', '.join(missing[:6]) if missing else 'None – all requirements are met'}. "
            f"Current coverage: {coverage}%."
        )
    elif any(k in q_lower for k in ["role", "suitable", "fit", "match", "recommend"]):
        ats = role_match.get("ats_score")
        fit = role_match.get("fit_label", "")
        target = role_match.get("role_name", "the target role")
        answer = (
            f"AI Role Match analysis for {target}: {fit}. "
            + (f"ATS Score: {ats}%. " if ats else "")
            + (role_match.get("match_explanation", "") or "")
        )
    elif any(k in q_lower for k in ["plan", "develop", "learn", "next", "path"]):
        phases = _build_phases(missing[:6])
        answer = (
            f"Recommended development path for {role_name}: "
            + " → ".join(p["name"] for p in phases)
            + f". Priority: {', '.join(missing[:3] or ['Expand core skills'])}."
        )
    elif any(k in q_lower for k in ["summarize", "summary", "about", "overview"]):
        exp = employee.get("experience_years", 0)
        dept = employee.get("department", "")
        answer = (
            f"{role_name} in {dept} with {exp} years' experience. "
            f"Skill coverage: {coverage}%. "
            f"Strong in: {', '.join(matching[:3] or current_skills[:3] or ['N/A'])}. "
            + (f"Development areas: {', '.join(missing[:3])}." if missing else "All required skills present.")
        )
    else:
        answer = (
            "I can help with questions about skills, gaps, role matches, and development plans. "
            "Try: 'What skills are missing?', 'What roles suit this employee?', or 'Generate a development plan'."
        )

    return {
        "source": "structured-analysis",
        "ai_available": False,
        "answer": answer,
        "question": question,
    }


def _template_summarize_employee(
    employee_data: Dict, skill_analysis: Optional[Dict]
) -> Dict[str, Any]:
    role = employee_data.get("role", "Professional")
    dept = employee_data.get("department", "General")
    exp = employee_data.get("experience_years", 1)
    skills = employee_data.get("current_skills", [])
    coverage = (skill_analysis or {}).get("coverage_percent", 0)
    matching = (skill_analysis or {}).get("matching_skills", [])

    top_skills = matching[:4] if matching else skills[:4]

    summary = (
        f"{role} in the {dept} department with {exp:.0f} year{'s' if exp != 1 else ''} of experience. "
        f"Demonstrates proficiency in {', '.join(top_skills) if top_skills else 'various competencies'}. "
    )
    if skill_analysis:
        summary += f"Role skill coverage: {coverage}%. "
        missing = skill_analysis.get("missing_skills", [])
        if missing:
            summary += f"Development opportunities identified in {', '.join(missing[:3])}."
        else:
            summary += "All required competencies for the current role are met."

    return {
        "source": "structured-analysis",
        "ai_available": False,
        "summary": summary,
    }


def _build_phases(skills: List[str]) -> List[Dict]:
    if not skills:
        return [{"phase": 1, "name": "Foundation Building", "skills": [], "weeks": 4}]

    chunk_size = max(1, (len(skills) + 2) // 3)
    chunks = [skills[i : i + chunk_size] for i in range(0, len(skills), chunk_size)]
    phase_names = ["Foundation", "Core Competency", "Advanced Application"]
    phases = []
    for idx, chunk in enumerate(chunks[:3]):
        phases.append({
            "phase": idx + 1,
            "name": phase_names[idx] if idx < len(phase_names) else f"Phase {idx+1}",
            "skills": chunk,
            "weeks": len(chunk) * 2,
        })
    return phases
