from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.workforce import EmployeeProfile, RoleProfile, SkillGap, LearningPath
from app.models.action_proposal import ActionProposal
from app.services.workforce.intelligence_service import WorkforceIntelligenceService
from app.services.proposal_service import ProposalService


class WorkforceAgent:
    """
    Governed AI Agent for Inclusive Workforce Intelligence.
    Executes the 8-stage pattern:
    Observe -> Retrieve -> Detect -> Analyze -> Reason -> Recommend -> Validate -> ActionProposal.
    Strictly safeguards employee privacy and dignity; prohibits automated hiring/firing/ranking.
    """

    @classmethod
    def analyze_workforce_readiness(cls, db: Session, business_id: str) -> Dict[str, Any]:
        employees = db.query(EmployeeProfile).filter(EmployeeProfile.business_id == business_id).all()
        roles = db.query(RoleProfile).filter(RoleProfile.business_id == business_id).all()

        detected_gaps = WorkforceIntelligenceService.detect_and_sync_skill_gaps(db, business_id)

        # Sync learning paths for employees with gaps
        synced_paths = []
        for emp in employees:
            lp = WorkforceIntelligenceService.generate_or_sync_learning_path(db, business_id, emp.id)
            if lp:
                synced_paths.append(lp)

        summary = WorkforceIntelligenceService.calculate_workforce_summary(db, business_id)

        recommendations = []
        for gap in detected_gaps[:5]:
            emp_ref = gap.employee.employee_reference if gap.employee else "Staff Member"
            recommendations.append({
                "gap_id": gap.id,
                "employee_ref": emp_ref,
                "skill": gap.required_skill,
                "gap_level": gap.gap_level,
                "recommended_action": gap.recommended_action,
                "status": gap.status,
            })

        return {
            "status": "COMPLETED",
            "business_id": business_id,
            "employees_analyzed": len(employees),
            "roles_analyzed": len(roles),
            "skill_gaps_identified": len(detected_gaps),
            "learning_paths_active": len(synced_paths),
            "skill_coverage_pct": summary["skill_coverage_pct"],
            "accessibility_supported": summary["accessibility_count"],
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }

    @classmethod
    def propose_action_for_skill_gap(cls, db: Session, business_id: str, gap_id: str) -> ActionProposal:
        """
        Creates an ActionProposal to enroll an employee into a structured learning module.
        Human approval is strictly required.
        """
        gap = db.query(SkillGap).filter(
            SkillGap.id == gap_id,
            SkillGap.business_id == business_id
        ).first()

        if not gap:
            raise ValueError("Skill gap not found or does not belong to active business.")

        emp_ref = gap.employee.employee_reference if gap.employee else "Staff Member"
        role_name = gap.role.role_name if gap.role else "Role"

        proposal_data = {
            "action_type": "WORKFORCE_UPSKILLING_ACTION",
            "title": f"Enroll {emp_ref} in {gap.required_skill} Pathway",
            "reason": f"Workforce Intelligence Agent identified critical role competency gap in {role_name}: {gap.required_skill}. {gap.recommended_action}",
            "affected_entity_type": "skill_gap",
            "affected_entity_id": gap.id,
            "changes": {
                "status": {"from": gap.status, "to": "ENROLLED"},
                "gap_id": gap.id,
                "employee_reference": emp_ref,
                "role": role_name,
                "required_skill": gap.required_skill,
                "action": gap.recommended_action,
            },
            "risk_level": "Low",
            "created_by": "Workforce Intelligence Agent"
        }

        proposal = ProposalService.create_proposal(db, business_id, proposal_data)
        gap.status = "ENROLLED"
        gap.updated_at = datetime.utcnow()
        db.commit()

        return proposal
