"""
Workforce AI Configuration
---------------------------
Reads model paths and feature flags from environment variables.
Falls back to project-relative paths pointing at the downloaded model repos.
"""
from __future__ import annotations

import os
from pathlib import Path

# Project root (two levels up from this file: backend/app/workforce_ai → backend/)
_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
# Repo root (one level above backend/)
_REPO_ROOT = _BACKEND_ROOT.parent.parent  # d:\SupplychainPowerHouseSAP


def _resolve(env_var: str, default_relative: str) -> str:
    """Return absolute path from env-var or default relative-to-repo-root path."""
    val = os.getenv(env_var)
    if val:
        return val
    candidate = _REPO_ROOT / default_relative
    return str(candidate)


# ──────────────────────────────────────────────────
# Feature flags
# ──────────────────────────────────────────────────
WORKFORCE_AI_ENABLED: bool = os.getenv("WORKFORCE_AI_ENABLED", "true").lower() == "true"

# ──────────────────────────────────────────────────
# Model paths (env-var override → project-relative default)
# ──────────────────────────────────────────────────
NUEXTRACT_MODEL_PATH: str = _resolve(
    "NUEXTRACT_MODEL_PATH",
    "NuExtract-tiny-Resume-Data-Extractor",
)

SKILL_SIM_MODEL_PATH: str = _resolve(
    "SKILL_SIM_MODEL_PATH",
    "skill-sim-model",
)

NBK_ATS_MODEL_PATH: str = _resolve(
    "NBK_ATS_MODEL_PATH",
    "nbk-ats-semantic-v1-en",
)

# Qwen3 – optional large model; set env-var if available locally
QWEN_MODEL_PATH: str = os.getenv("QWEN_MODEL_PATH", "")
# Qwen is only available if the env var is set AND the path exists
QWEN_AVAILABLE: bool = bool(QWEN_MODEL_PATH and Path(QWEN_MODEL_PATH).exists())

# ──────────────────────────────────────────────────
# Inference settings
# ──────────────────────────────────────────────────
DEVICE: str = os.getenv("WORKFORCE_AI_DEVICE", "auto")  # auto | cpu | cuda
MAX_RESUME_CHARS: int = int(os.getenv("WORKFORCE_AI_MAX_RESUME_CHARS", "12000"))
SKILL_SIM_THRESHOLD: float = float(os.getenv("SKILL_SIM_THRESHOLD", "0.55"))
