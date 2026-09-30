import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.action_proposal import ActionProposal
from app.models.audit_log import AuditLog
from app.models.document import Document
from app.models.compliance_task import ComplianceTask
from app.models.approval import Approval


class ProposalService:
    @staticmethod
    def get_proposals(db: Session, business_profile_id: str) -> List[ActionProposal]:
        return db.query(ActionProposal).filter(
            ActionProposal.business_profile_id == business_profile_id
        ).order_by(ActionProposal.created_at.desc()).all()

    @staticmethod
    def create_proposal(db: Session, business_profile_id: str, data: Dict[str, Any]) -> ActionProposal:
        proposal = ActionProposal(
            id=str(uuid.uuid4()),
            business_profile_id=business_profile_id,
            action_type=data.get("action_type", "UPDATE_STATUS"),
            title=data.get("title", "Proposed Operational Action"),
            reason=data.get("reason", "AI automated recommendation requiring human confirmation."),
            affected_entity_type=data.get("affected_entity_type", "document"),
            affected_entity_id=data.get("affected_entity_id"),
            changes=data.get("changes", {}),
            risk_level=data.get("risk_level", "Low"),
            status="Pending Review",
            created_by=data.get("created_by", "AI Compliance Advisor")
        )
        db.add(proposal)
        db.commit()
        db.refresh(proposal)
        return proposal

    @staticmethod
    def confirm_proposal(
        db: Session,
        business_profile_id: str,
        proposal_id: str,
        confirmed_by: str = "Mohith K"
    ) -> Dict[str, Any]:
        proposal = db.query(ActionProposal).filter(
            ActionProposal.id == proposal_id,
            ActionProposal.business_profile_id == business_profile_id
        ).first()

        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Action proposal not found or does not belong to this business profile."
            )

        if proposal.status != "Pending Review":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Proposal has already been processed with status: {proposal.status}"
            )

        entity_type = proposal.affected_entity_type.lower()
        entity_name = proposal.title
        prev_state = "Pending"
        new_state = "Verified"

        changes = proposal.changes or {}
        if "status" in changes and isinstance(changes["status"], dict):
            prev_state = changes["status"].get("from", prev_state)
            new_state = changes["status"].get("to", new_state)

        # Execute safe mutation on the targeted entity
        if entity_type == "document":
            doc = None
            if proposal.affected_entity_id:
                doc = db.query(Document).filter(
                    Document.id == proposal.affected_entity_id,
                    Document.business_profile_id == business_profile_id
                ).first()
            if not doc:
                doc = db.query(Document).filter(
                    Document.business_profile_id == business_profile_id,
                    Document.name.ilike(f"%{proposal.title[:20]}%")
                ).first()
            if doc:
                entity_name = doc.name
                prev_state = doc.status
                doc.status = new_state
                doc.updated_at = datetime.utcnow()
                db.add(doc)

        elif entity_type == "task":
            task = None
            if proposal.affected_entity_id:
                task = db.query(ComplianceTask).filter(
                    ComplianceTask.id == proposal.affected_entity_id,
                    ComplianceTask.business_profile_id == business_profile_id
                ).first()
            if not task:
                task = db.query(ComplianceTask).filter(
                    ComplianceTask.business_profile_id == business_profile_id,
                    ComplianceTask.title.ilike(f"%{proposal.title[:20]}%")
                ).first()
            if task:
                entity_name = task.title
                prev_state = task.status
                task.status = new_state
                task.completed = (new_state.lower() in ["completed", "verified", "closed"])
                task.updated_at = datetime.utcnow()
                db.add(task)

        elif entity_type == "approval":
            app = None
            if proposal.affected_entity_id:
                app = db.query(Approval).filter(
                    Approval.id == proposal.affected_entity_id,
                    Approval.business_profile_id == business_profile_id
                ).first()
            if not app:
                app = db.query(Approval).filter(
                    Approval.business_profile_id == business_profile_id,
                    Approval.name.ilike(f"%{proposal.title[:20]}%")
                ).first()
            if app:
                entity_name = app.name
                prev_state = app.status
                app.status = new_state
                app.updated_at = datetime.utcnow()
                db.add(app)

        elif entity_type in ["green_opportunity", "green"]:
            from app.models.green_opportunity import GreenOpportunity
            opp = None
            if proposal.affected_entity_id:
                opp = db.query(GreenOpportunity).filter(
                    GreenOpportunity.id == proposal.affected_entity_id,
                    GreenOpportunity.business_profile_id == business_profile_id
                ).first()
            if opp:
                entity_name = opp.title
                prev_state = opp.status
                opp.status = "TASK_CREATED"
                opp.approved_at = datetime.utcnow()
                db.add(opp)

                # Create a governed Compliance Task in the existing task system
                new_task = ComplianceTask(
                    id=str(uuid.uuid4()),
                    business_profile_id=business_profile_id,
                    title=f"[Green Ops] {opp.title}",
                    description=opp.recommended_action,
                    category="Green Operations",
                    priority=opp.priority,
                    status="Upcoming",
                    due_date="Due in 14 days",
                    estimated_days=14,
                    assignee=confirmed_by,
                )
                db.add(new_task)
                new_state = "TASK_CREATED"

        elif entity_type in ["supply_chain_risk", "supply_risk", "supplier"]:
            from app.models.supplier import SupplyChainRisk
            risk = None
            if proposal.affected_entity_id:
                risk = db.query(SupplyChainRisk).filter(
                    SupplyChainRisk.id == proposal.affected_entity_id,
                    SupplyChainRisk.business_id == business_profile_id
                ).first()
            if risk:
                entity_name = risk.title
                prev_state = risk.status
                risk.status = "ACTION_CREATED"
                risk.updated_at = datetime.utcnow()
                db.add(risk)

                new_task = ComplianceTask(
                    id=str(uuid.uuid4()),
                    business_profile_id=business_profile_id,
                    title=f"[Supply Chain] {risk.title}",
                    description=risk.recommended_action,
                    category="Supply Chain Resilience",
                    priority=risk.priority,
                    status="Upcoming",
                    due_date="Due in 14 days",
                    estimated_days=14,
                    assignee=confirmed_by,
                )
                db.add(new_task)
                new_state = "ACTION_CREATED"

        elif entity_type in ["skill_gap", "learning_path", "workforce"]:
            from app.models.workforce import SkillGap, LearningPath
            gap = None
            if proposal.affected_entity_id:
                gap = db.query(SkillGap).filter(
                    SkillGap.id == proposal.affected_entity_id,
                    SkillGap.business_id == business_profile_id
                ).first()
            if gap:
                entity_name = f"Upskill {gap.required_skill}"
                prev_state = gap.status
                gap.status = "ENROLLED"
                gap.updated_at = datetime.utcnow()
                db.add(gap)

                new_task = ComplianceTask(
                    id=str(uuid.uuid4()),
                    business_profile_id=business_profile_id,
                    title=f"[Workforce] Upskill: {gap.required_skill}",
                    description=gap.recommended_action,
                    category="Workforce Intelligence",
                    priority="Medium",
                    status="Upcoming",
                    due_date="Due in 21 days",
                    estimated_days=21,
                    assignee=confirmed_by,
                )
                db.add(new_task)
                new_state = "ENROLLED"

        # Update proposal state
        proposal.status = "Executed"
        proposal.confirmed_by = confirmed_by
        proposal.updated_at = datetime.utcnow()
        db.add(proposal)

        # Record immutable Audit Log
        audit = AuditLog(
            id=str(uuid.uuid4()),
            business_profile_id=business_profile_id,
            user_name=confirmed_by,
            action=proposal.action_type,
            target_entity_type=proposal.affected_entity_type,
            target_entity_name=entity_name,
            previous_state=prev_state,
            new_state=new_state,
            source=f"Action Proposal #{proposal.id[:8]} (Confirmed by Human)",
            proposal_id=proposal.id,
            timestamp=datetime.utcnow(),
            details=proposal.changes
        )
        db.add(audit)
        db.commit()
        db.refresh(proposal)
        db.refresh(audit)

        return {
            "success": True,
            "message": f"Action '{proposal.title}' successfully executed and audited.",
            "id": proposal.id,
            "status": "Confirmed",
            "confirmed_by": proposal.confirmed_by,
            "confirmed_at": proposal.updated_at.isoformat(),
            "proposal": {
                "id": proposal.id,
                "status": "Confirmed",
                "confirmed_by": proposal.confirmed_by,
                "confirmed_at": proposal.updated_at.isoformat(),
                "updated_at": proposal.updated_at.isoformat()
            },
            "audit_log": {
                "id": audit.id,
                "user_name": audit.user_name,
                "action": audit.action,
                "action_type": audit.action,
                "action_name": audit.target_entity_name,
                "action_status": "COMPLETED",
                "target_entity_name": audit.target_entity_name,
                "previous_state": audit.previous_state,
                "new_state": audit.new_state,
                "timestamp": audit.timestamp.isoformat()
            }
        }
