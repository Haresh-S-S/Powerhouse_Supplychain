import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    # Privacy-preserving employee reference ID (e.g. EMP-201) rather than exposing sensitive personal info
    employee_reference = Column(String(100), nullable=False, index=True)
    role = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    experience_years = Column(Float, nullable=False, default=1.0)
    current_skills = Column(JSON, nullable=False, default=list)  # list of skill names/levels
    preferred_learning_areas = Column(JSON, nullable=False, default=list)
    employment_status = Column(String(50), nullable=False, default="Active")
    accessibility_preferences = Column(JSON, nullable=False, default=list)  # ["Screen Reader Compatible", "Captioned Video", "Self-Paced Audio"]
    is_demo = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="employee_profiles")
    skill_gaps = relationship("SkillGap", back_populates="employee", cascade="all, delete-orphan")
    learning_paths = relationship("LearningPath", back_populates="employee", cascade="all, delete-orphan")


class RoleProfile(Base):
    __tablename__ = "role_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    role_name = Column(String(100), nullable=False, index=True)
    department = Column(String(100), nullable=False)
    required_skills = Column(JSON, nullable=False, default=list)  # [{"skill": "Data Analysis", "level": "Intermediate", "category": "Digital"}]
    optional_skills = Column(JSON, nullable=False, default=list)
    is_demo = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="role_profiles")
    skill_gaps = relationship("SkillGap", back_populates="role")

    @property
    def criticality(self) -> str:
        name_dept = f"{self.role_name} {self.department}".lower()
        if any(kw in name_dept for kw in ["supervisor", "lead", "officer", "inspector", "safety", "operator", "head", "technician", "manager", "chef"]):
            return "Critical"
        return "Standard"


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(String(36), ForeignKey("employee_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(String(36), ForeignKey("role_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    current_skill = Column(String(100), nullable=True)
    required_skill = Column(String(100), nullable=False)
    gap_level = Column(String(50), nullable=False, default="Medium")  # High, Medium, Low
    recommended_action = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="IDENTIFIED")  # IDENTIFIED, RECOMMENDED, ENROLLED, IN_PROGRESS, RESOLVED, WAIVED
    is_demo = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="skill_gaps")
    employee = relationship("EmployeeProfile", back_populates="skill_gaps")
    role = relationship("RoleProfile", back_populates="skill_gaps")


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(String(36), ForeignKey("employee_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    target_role = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    skill_sequence = Column(JSON, nullable=False, default=list)  # [{"step": 1, "skill": "...", "duration": "2 weeks", "format": "Captioned Video"}]
    progress = Column(Float, nullable=False, default=0.0)  # 0.0 to 100.0 %
    status = Column(String(50), nullable=False, default="RECOMMENDED")  # RECOMMENDED, ACTIVE, COMPLETED, ON_HOLD
    estimated_weeks = Column(Integer, nullable=False, default=4)
    accessibility_accommodations = Column(JSON, nullable=False, default=list)
    is_demo = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="learning_paths")
    employee = relationship("EmployeeProfile", back_populates="learning_paths")
