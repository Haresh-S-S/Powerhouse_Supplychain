"""
Workforce AI Schemas
--------------------
Pydantic schemas for the AI-powered Workforce endpoints.
Extends the existing workforce schemas without modifying them.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────────────────────────
# Resume Analysis
# ──────────────────────────────────────────────────────────────────────────────

class ResumeAnalysisResponse(BaseModel):
    """Structured output from NuExtract resume extraction."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[Dict[str, str]] = Field(default_factory=list)
    education: List[Dict[str, str]] = Field(default_factory=list)
    other_details: List[str] = Field(default_factory=list)
    ai_available: bool = True
    error: Optional[str] = None


# ──────────────────────────────────────────────────────────────────────────────
# Skill Intelligence
# ──────────────────────────────────────────────────────────────────────────────

class SkillPair(BaseModel):
    required: str
    best_match: Optional[str] = None
    score: float
    status: str  # match | related | missing


class SkillGapAnalysisRequest(BaseModel):
    employee_id: Optional[str] = None
    employee_skills: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    role_name: Optional[str] = None


class SkillGapAnalysisResponse(BaseModel):
    employee_id: Optional[str] = None
    role_name: Optional[str] = None
    matching_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    related_skills: List[str] = Field(default_factory=list)
    coverage_percent: int = 0
    skill_pairs: List[SkillPair] = Field(default_factory=list)
    explanation: Optional[str] = None
    ai_available: bool = True


# ──────────────────────────────────────────────────────────────────────────────
# Role Matching
# ──────────────────────────────────────────────────────────────────────────────

class RoleMatchRequest(BaseModel):
    employee_id: str
    role_id: Optional[str] = None
    role_name: Optional[str] = None
    role_description: Optional[str] = None


class RoleMatchResponse(BaseModel):
    employee_id: str
    role_name: str
    ats_score: Optional[float] = None
    semantic_similarity: Optional[float] = None
    fit_label: str
    match_explanation: str
    matching_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    related_skills: List[str] = Field(default_factory=list)
    skill_coverage_percent: int = 0
    ai_available: bool = True


# ──────────────────────────────────────────────────────────────────────────────
# Career Recommendations
# ──────────────────────────────────────────────────────────────────────────────

class CareerRecommendationRequest(BaseModel):
    employee_id: str
    target_role_id: Optional[str] = None
    target_role_name: Optional[str] = None


class DevelopmentPhase(BaseModel):
    phase: int
    name: str
    skills: List[str]
    weeks: int


class CareerRecommendationResponse(BaseModel):
    employee_id: str
    current_role: str
    target_role: str
    experience_years: float
    current_strengths: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    priority_skills: List[str] = Field(default_factory=list)
    development_phases: List[DevelopmentPhase] = Field(default_factory=list)
    summary: str = ""
    ats_match_note: Optional[str] = None
    source: str = "structured-analysis"
    ai_available: bool = True


# ──────────────────────────────────────────────────────────────────────────────
# Development Plan
# ──────────────────────────────────────────────────────────────────────────────

class DevelopmentPlanRequest(BaseModel):
    employee_id: str
    target_role_name: str


class DevelopmentPlanResponse(BaseModel):
    employee_id: str
    current_role: str
    target_role: str
    estimated_weeks: int
    phases: List[DevelopmentPhase] = Field(default_factory=list)
    summary: str = ""
    source: str = "structured-analysis"
    ai_available: bool = True


# ──────────────────────────────────────────────────────────────────────────────
# Employee AI Analysis
# ──────────────────────────────────────────────────────────────────────────────

class EmployeeAIAnalysisResponse(BaseModel):
    employee_id: str
    employee_reference: str
    current_role: str
    department: str
    experience_years: float
    current_skills: List[str] = Field(default_factory=list)
    skill_coverage_percent: int = 0
    matching_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    related_skills: List[str] = Field(default_factory=list)
    ai_summary: str = ""
    career_recommendation: Optional[Dict[str, Any]] = None
    potential_roles: List[Dict[str, Any]] = Field(default_factory=list)
    ai_available: bool = True


# ──────────────────────────────────────────────────────────────────────────────
# Workforce AI Chat
# ──────────────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    employee_id: Optional[str] = None
    business_profile_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    question: str
    answer: str
    source: str = "structured-analysis"
    ai_available: bool = True
    suggested_actions: List[str] = Field(default_factory=list)
