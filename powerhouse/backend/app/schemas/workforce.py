from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class EmployeeProfileBase(BaseModel):
    employee_reference: str  # e.g. "EMP-102"
    role: str
    department: str
    experience_years: float = 1.0
    current_skills: List[str] = Field(default_factory=list)
    preferred_learning_areas: List[str] = Field(default_factory=list)
    employment_status: str = "Active"
    accessibility_preferences: List[str] = Field(default_factory=list)


class EmployeeProfileCreate(EmployeeProfileBase):
    pass


class EmployeeProfileResponse(EmployeeProfileBase):
    id: str
    business_id: str
    is_demo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoleProfileBase(BaseModel):
    role_name: str
    department: str
    criticality: Optional[str] = "Critical"
    required_skills: List[Any] = Field(default_factory=list)
    optional_skills: List[Any] = Field(default_factory=list)


class RoleProfileCreate(RoleProfileBase):
    pass


class RoleProfileResponse(RoleProfileBase):
    id: str
    business_id: str
    is_demo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SkillGapResponse(BaseModel):
    id: str
    business_id: str
    employee_id: str
    role_id: str
    employee_reference: Optional[str] = None
    role_name: Optional[str] = None
    department: Optional[str] = None
    current_skill: Optional[str] = None
    required_skill: str
    gap_level: str  # High, Medium, Low
    recommended_action: str
    status: str  # IDENTIFIED, RECOMMENDED, ENROLLED, IN_PROGRESS, RESOLVED
    accessibility_accommodations: List[str] = Field(default_factory=list)
    is_demo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LearningPathResponse(BaseModel):
    id: str
    business_id: str
    employee_id: str
    employee_reference: Optional[str] = None
    target_role: str
    title: str
    skill_sequence: List[Dict[str, Any]] = Field(default_factory=list)
    progress: float
    status: str  # RECOMMENDED, ACTIVE, COMPLETED, ON_HOLD
    estimated_weeks: int
    accessibility_accommodations: List[str] = Field(default_factory=list)
    is_demo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkforceSummaryResponse(BaseModel):
    business_id: str
    total_employees: int
    total_roles: int
    open_skill_gaps_count: int
    active_learning_paths_count: int
    average_skill_coverage_percent: int  # 0 to 100
    accessibility_supported_count: int
    top_skill_gaps: List[SkillGapResponse] = Field(default_factory=list)
    active_paths: List[LearningPathResponse] = Field(default_factory=list)
