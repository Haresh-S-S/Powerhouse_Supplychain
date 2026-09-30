"""
NuExtract Adapter
-----------------
Wraps the local NuExtract-tiny-Resume-Data-Extractor model for structured
resume / CV information extraction.

The model is a fine-tuned Qwen2.5-0.5B (LoRA) available as:
  • GGUF weights (Q4_K_M) → best used via Ollama
  • SafeTensors adapter weights → usable via `transformers` + `peft`

Strategy used here:
  1. Try `transformers` + `peft` inference (CPU or CUDA) with lazy loading.
  2. If model weights / packages are unavailable, return a graceful error dict
     so the rest of PowerHouse keeps running.

The adapter is a singleton; heavy model state is only loaded once and reused.
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional

logger = logging.getLogger("[WORKFORCE AI]")

_TEMPLATE = json.dumps(
    {
        "name": "",
        "email": "",
        "phone": "",
        "website": "",
        "skills": [""],
        "experience": [{"title": "", "company": "", "duration": ""}],
        "education": [{"degree": "", "institution": "", "year": ""}],
        "other_details": [""],
    },
    indent=4,
)

# Canonical casing map for common skills (NuExtract uses .title() during training)
_CASING_MAP: Dict[str, str] = {
    "fastapi": "FastAPI",
    "api": "API",
    "sql": "SQL",
    "nosql": "NoSQL",
    "html": "HTML",
    "css": "CSS",
    "aws": "AWS",
    "gcp": "GCP",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "restapi": "REST API",
    "rest api": "REST API",
    "ml": "Machine Learning",
    "ai": "AI",
    "nlp": "NLP",
    "llm": "LLM",
    "js": "JavaScript",
    "ts": "TypeScript",
    "kubernetes": "Kubernetes",
    "dockerfile": "Docker",
}


def _fix_casing(skill: str) -> str:
    lower = skill.lower().strip()
    return _CASING_MAP.get(lower, skill.strip())


def _extract_first_json(text: str) -> str:
    """Brace-counting extraction as documented in the model README."""
    depth = 0
    start: Optional[int] = None
    for i, ch in enumerate(text):
        if ch == "{":
            if start is None:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                return text[start : i + 1]
    return text


def _normalize_profile(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize the raw model output into our PowerHouse schema."""
    name = raw.get("name") or None
    email = raw.get("email") or None
    phone = raw.get("phone") or None
    website = raw.get("website") or None

    skills_raw = raw.get("skills") or []
    skills = []
    for s in skills_raw:
        if isinstance(s, str) and s.strip():
            skills.append(_fix_casing(s))

    experience_raw = raw.get("experience") or []
    experience = []
    for e in experience_raw:
        if isinstance(e, dict):
            title = (e.get("title") or "").strip()
            company = (e.get("company") or "").strip()
            duration = (e.get("duration") or "").strip()
            if title or company:
                experience.append({"title": title, "company": company, "duration": duration})

    education_raw = raw.get("education") or []
    education = []
    for ed in education_raw:
        if isinstance(ed, dict):
            degree = (ed.get("degree") or "").strip()
            institution = (ed.get("institution") or "").strip()
            year = (ed.get("year") or "").strip()
            if degree or institution:
                education.append({"degree": degree, "institution": institution, "year": year})

    other_details = [d for d in (raw.get("other_details") or []) if isinstance(d, str) and d.strip()]

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "website": website,
        "skills": skills,
        "experience": experience,
        "education": education,
        "other_details": other_details,
    }


class NuExtractAdapter:
    """
    Singleton adapter for NuExtract-tiny-Resume-Data-Extractor.
    Lazy-loads the model on first use.
    """

    _instance: Optional["NuExtractAdapter"] = None
    _lock = Lock()

    def __init__(self) -> None:
        self._model = None
        self._tokenizer = None
        self._device: Optional[str] = None
        self._available: Optional[bool] = None  # None = not yet tried
        self._load_lock = Lock()

    @classmethod
    def get(cls) -> "NuExtractAdapter":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def _try_load(self) -> bool:
        """Attempt to load model weights. Returns True on success."""
        from app.workforce_ai.config import NUEXTRACT_MODEL_PATH

        model_path = Path(NUEXTRACT_MODEL_PATH)
        if not model_path.exists():
            logger.warning(
                f"[WORKFORCE AI] NuExtract model path not found: {model_path}. "
                "Resume extraction will be unavailable."
            )
            return False

        try:
            import torch  # noqa: F401
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from peft import PeftModel  # noqa: F401

            logger.info(f"[WORKFORCE AI] Loading NuExtract from {model_path} …")

            # Detect device
            if torch.cuda.is_available():
                device = "cuda"
                dtype = torch.bfloat16
            else:
                device = "cpu"
                dtype = torch.float32

            # NuExtract-tiny-v1.5 base model identifier
            base_model_id = "numind/NuExtract-tiny-v1.5"

            tokenizer = AutoTokenizer.from_pretrained(
                str(model_path), trust_remote_code=True
            )
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_id,
                torch_dtype=dtype,
                trust_remote_code=True,
            )
            model = PeftModel.from_pretrained(base_model, str(model_path))
            model = model.merge_and_unload().to(device).eval()

            self._model = model
            self._tokenizer = tokenizer
            self._device = device
            logger.info(f"[WORKFORCE AI] NuExtract loaded on {device}")
            return True

        except ImportError as e:
            logger.warning(
                f"[WORKFORCE AI] NuExtract requires `transformers`, `peft`, `torch`. "
                f"Missing: {e}. Resume extraction unavailable."
            )
            return False
        except Exception as e:
            logger.error(f"[WORKFORCE AI] NuExtract load failed: {e}")
            return False

    def _ensure_loaded(self) -> bool:
        """Lazy-load on first call, thread-safe."""
        if self._available is None:
            with self._load_lock:
                if self._available is None:
                    self._available = self._try_load()
        return self._available

    def extract(self, resume_text: str) -> Dict[str, Any]:
        """
        Extract structured profile from raw resume text.
        Returns a normalized dict or an error dict.
        """
        if not self._ensure_loaded():
            return {
                "error": "NuExtract model unavailable",
                "ai_unavailable": True,
                "name": None,
                "email": None,
                "phone": None,
                "website": None,
                "skills": [],
                "experience": [],
                "education": [],
                "other_details": [],
            }

        import torch

        from app.workforce_ai.config import MAX_RESUME_CHARS

        resume_text = resume_text[:MAX_RESUME_CHARS]

        prompt = (
            "<|input|>\n"
            f"### Template:\n{_TEMPLATE}\n"
            f"### Text:\n{resume_text}\n\n"
            "<|output|>"
        )

        try:
            inputs = self._tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048,
            ).to(self._device)

            with torch.no_grad():
                out = self._model.generate(
                    **inputs,
                    max_new_tokens=600,
                    do_sample=False,
                )

            decoded = self._tokenizer.decode(out[0], skip_special_tokens=True)
            raw_text = decoded.split("<|output|>")[-1].strip()
            json_str = _extract_first_json(raw_text)
            raw_dict = json.loads(json_str)
            return _normalize_profile(raw_dict)

        except json.JSONDecodeError as e:
            logger.error(f"[WORKFORCE AI] NuExtract JSON parse error: {e}")
            return {
                "error": "Could not parse model output as JSON",
                "ai_unavailable": False,
                "name": None,
                "email": None,
                "phone": None,
                "website": None,
                "skills": [],
                "experience": [],
                "education": [],
                "other_details": [],
            }
        except Exception as e:
            logger.error(f"[WORKFORCE AI] NuExtract inference error: {e}")
            return {
                "error": f"Model inference error: {type(e).__name__}",
                "ai_unavailable": False,
                "name": None,
                "email": None,
                "phone": None,
                "website": None,
                "skills": [],
                "experience": [],
                "education": [],
                "other_details": [],
            }
