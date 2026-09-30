"""
Resume Service
--------------
Orchestrates the full resume processing pipeline:
  PDF text extraction → NuExtract → normalization → skill-sim analysis
"""
from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict

logger = logging.getLogger("[WORKFORCE AI]")


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract plain text from PDF file bytes using pypdf."""
    try:
        import io
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
        return "\n".join(pages_text)
    except ImportError:
        logger.error("[WORKFORCE AI] pypdf not installed – cannot extract PDF text")
        return ""
    except Exception as e:
        logger.error(f"[WORKFORCE AI] PDF extraction error: {e}")
        return ""


def analyze_resume(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Full resume analysis pipeline:
      1. Extract PDF text
      2. Run NuExtract for structured profile
      3. Return normalized profile

    Returns a dict matching ResumeAnalysisResponse schema.
    """
    from app.workforce_ai.adapters.nuextract_adapter import NuExtractAdapter

    logger.info("[WORKFORCE AI] Running resume analysis …")

    # Step 1: Text extraction
    resume_text = extract_text_from_pdf_bytes(pdf_bytes)
    if not resume_text.strip():
        return {
            "name": None,
            "email": None,
            "phone": None,
            "website": None,
            "skills": [],
            "experience": [],
            "education": [],
            "other_details": [],
            "ai_available": False,
            "error": "Could not extract text from the uploaded file.",
        }

    # Step 2: NuExtract inference
    adapter = NuExtractAdapter.get()
    result = adapter.extract(resume_text)
    logger.info(
        f"[WORKFORCE AI] Resume analysis complete. "
        f"Skills found: {len(result.get('skills', []))}"
    )
    return result


def resume_hash(pdf_bytes: bytes) -> str:
    """SHA-256 hash of PDF content – used for deduplication caching."""
    return hashlib.sha256(pdf_bytes).hexdigest()
