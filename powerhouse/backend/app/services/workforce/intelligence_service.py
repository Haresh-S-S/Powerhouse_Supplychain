import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.workforce import EmployeeProfile, RoleProfile, SkillGap, LearningPath


class WorkforceIntelligenceService:
    @staticmethod
    def calculate_workforce_summary(db: Session, business_id: str) -> Dict[str, Any]:
        """
        Calculates deterministic skill coverage and workforce readiness metrics.
        Strictly respectful of employee privacy and dignity without punitive evaluations.
        """
        employees = db.query(EmployeeProfile).filter(EmployeeProfile.business_id == business_id).all()
        roles = db.query(RoleProfile).filter(RoleProfile.business_id == business_id).all()
        skill_gaps = db.query(SkillGap).filter(
            SkillGap.business_id == business_id,
            SkillGap.status.notin_(["RESOLVED", "WAIVED"])
        ).all()
        learning_paths = db.query(LearningPath).filter(
            LearningPath.business_id == business_id
        ).all()

        total_emps = len(employees)
        total_roles = len(roles)

        if total_emps == 0 or total_roles == 0:
            return {
                "total_employees": total_emps,
                "total_roles": total_roles,
                "open_skill_gaps": len(skill_gaps),
                "active_paths": len(learning_paths),
                "skill_coverage_pct": 75,
                "accessibility_count": 0
            }

        # Calculate coverage percentage
        total_required_skills = 0
        satisfied_skills = 0

        for emp in employees:
            matching_role = next((r for r in roles if r.role_name.lower() == emp.role.lower()), None)
            if matching_role:
                req_list = matching_role.required_skills or []
                total_required_skills += len(req_list)
                emp_skills = [s.lower() for s in (emp.current_skills or [])]
                for req in req_list:
                    req_name = (req.get("skill") if isinstance(req, dict) else str(req)).lower()
                    if any(req_name in es or es in req_name for es in emp_skills):
                        satisfied_skills += 1

        coverage_pct = (
            int(round((satisfied_skills / total_required_skills) * 100))
            if total_required_skills > 0 else 80
        )

        accessibility_count = len([e for e in employees if e.accessibility_preferences and len(e.accessibility_preferences) > 0])

        return {
            "total_employees": total_emps,
            "total_roles": total_roles,
            "open_skill_gaps": len(skill_gaps),
            "active_paths": len([p for p in learning_paths if p.status in ["ACTIVE", "RECOMMENDED"]]),
            "skill_coverage_pct": min(100, max(20, coverage_pct)),
            "accessibility_count": accessibility_count
        }

    @staticmethod
    def detect_and_sync_skill_gaps(db: Session, business_id: str) -> List[SkillGap]:
        """
        Compares employee skill sets against target role benchmark competencies.
        Generates constructive, explainable learning actions.
        """
        employees = db.query(EmployeeProfile).filter(EmployeeProfile.business_id == business_id).all()
        roles = db.query(RoleProfile).filter(RoleProfile.business_id == business_id).all()

        detected_gaps = []

        for emp in employees:
            matching_role = next((r for r in roles if r.role_name.lower() == emp.role.lower()), None)
            if not matching_role and roles:
                matching_role = roles[0]

            if not matching_role:
                continue

            emp_skills = [s.lower() for s in (emp.current_skills or [])]
            req_list = matching_role.required_skills or []

            for req in req_list:
                req_name = req.get("skill") if isinstance(req, dict) else str(req)
                category = req.get("category", "Operational Competency") if isinstance(req, dict) else "General"
                level = req.get("level", "Standard") if isinstance(req, dict) else "Standard"

                is_present = any(req_name.lower() in es or es in req_name.lower() for es in emp_skills)

                if not is_present:
                    existing = db.query(SkillGap).filter(
                        SkillGap.business_id == business_id,
                        SkillGap.employee_id == emp.id,
                        SkillGap.role_id == matching_role.id,
                        SkillGap.required_skill == req_name,
                        SkillGap.status.notin_(["RESOLVED", "WAIVED"])
                    ).first()

                    # Accommodations check
                    accommodations = emp.accessibility_preferences or []
                    acc_note = f" Format: {', '.join(accommodations)}" if accommodations else ""

                    if not existing:
                        gap = SkillGap(
                            id=str(uuid.uuid4()),
                            business_id=business_id,
                            employee_id=emp.id,
                            role_id=matching_role.id,
                            current_skill=None,
                            required_skill=req_name,
                            gap_level="High" if level in ["Advanced", "Critical"] else "Medium",
                            recommended_action=f"Enroll {emp.employee_reference} in structured {req_name} module ({category}).{acc_note}",
                            status="RECOMMENDED",
                            is_demo=emp.is_demo,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                        )
                        db.add(gap)
                        detected_gaps.append(gap)
                    else:
                        detected_gaps.append(existing)

        db.commit()
        return detected_gaps

    @staticmethod
    def generate_or_sync_learning_path(db: Session, business_id: str, employee_id: str) -> Optional[LearningPath]:
        """
        Builds a customized learning pathway for an employee to close open skill gaps.
        Incorporates accessibility preferences directly into sequence metadata.
        """
        emp = db.query(EmployeeProfile).filter(
            EmployeeProfile.id == employee_id,
            EmployeeProfile.business_id == business_id
        ).first()

        if not emp:
            return None

        open_gaps = db.query(SkillGap).filter(
            SkillGap.business_id == business_id,
            SkillGap.employee_id == emp.id,
            SkillGap.status.notin_(["RESOLVED", "WAIVED"])
        ).all()

        if not open_gaps:
            return None

        existing_path = db.query(LearningPath).filter(
            LearningPath.business_id == business_id,
            LearningPath.employee_id == emp.id,
            LearningPath.status.in_(["RECOMMENDED", "ACTIVE"])
        ).first()

        accommodations = emp.accessibility_preferences or ["Self-Paced Practice"]
        sequence = []
        for idx, gap in enumerate(open_gaps, start=1):
            sequence.append({
                "step": idx,
                "skill": gap.required_skill,
                "duration_weeks": 2,
                "accommodations": accommodations,
                "milestone": f"Demonstrate practical proficiency in {gap.required_skill}",
                "status": "In Progress" if idx == 1 else "Queued"
            })

        title = f"Professional Upskilling Pathway: {emp.role} ({emp.employee_reference})"
        estimated_weeks = max(4, len(sequence) * 2)

        if not existing_path:
            path = LearningPath(
                id=str(uuid.uuid4()),
                business_id=business_id,
                employee_id=emp.id,
                target_role=emp.role,
                title=title,
                skill_sequence=sequence,
                progress=15.0 if sequence else 0.0,
                status="ACTIVE",
                estimated_weeks=estimated_weeks,
                accessibility_accommodations=accommodations,
                is_demo=emp.is_demo,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(path)
            db.commit()
            return path
        else:
            existing_path.skill_sequence = sequence
            existing_path.estimated_weeks = estimated_weeks
            existing_path.accessibility_accommodations = accommodations
            existing_path.updated_at = datetime.utcnow()
            db.commit()
            return existing_path
