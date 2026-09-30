"""
Human-in-the-Loop Approval & Audit Trail Service
------------------------------------------------
Provides:
1. Management of high-impact AI recommendations awaiting human approval
2. Decision gate execution (APPROVE / REJECT with reason)
3. Audit log persistence and retrieval
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.supply_chain_tower import AIRecommendation, SupplyChainAudit


class HumanApprovalService:

    @staticmethod
    def get_pending_recommendations(db: Session, business_id: str) -> List[Dict[str, Any]]:
        """Fetch all AI recommendations with their approval statuses."""
        recs = db.query(AIRecommendation).filter(
            AIRecommendation.business_id == business_id
        ).order_by(AIRecommendation.created_at.desc()).all()

        res = []
        for r in recs:
            res.append({
                "id": r.id,
                "title": r.title,
                "recommendation_type": r.recommendation_type,
                "description": r.description,
                "expected_cost_usd": r.expected_cost_usd,
                "expected_delay_reduction_days": r.expected_delay_reduction_days,
                "expected_risk_reduction_pct": r.expected_risk_reduction_pct,
                "requires_human_approval": r.requires_human_approval,
                "approval_status": r.approval_status,  # PENDING, APPROVED, REJECTED
                "approved_by": r.approved_by,
                "approved_at": r.approved_at.strftime("%Y-%m-%d %H:%M UTC") if r.approved_at else None,
                "rejection_reason": r.rejection_reason,
                "explanation_why": r.explanation_why,
                "action_payload": r.action_payload or {},
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M UTC"),
            })
        return res

    @staticmethod
    def process_decision(
        db: Session,
        business_id: str,
        recommendation_id: str,
        decision: str,  # "APPROVED" or "REJECTED"
        decided_by: str = "Supply Chain Operations Lead",
        rejection_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record human sign-off or rejection of a critical AI recommendation."""
        rec = db.query(AIRecommendation).filter(
            AIRecommendation.id == recommendation_id,
            AIRecommendation.business_id == business_id,
        ).first()

        if not rec:
            raise ValueError("Recommendation record not found")

        rec.approval_status = decision.upper()
        if decision.upper() == "APPROVED":
            rec.approved_by = decided_by
            rec.approved_at = datetime.utcnow()
            rec.rejection_reason = None
            audit_action = f"Human Approved AI Recommendation: {rec.title}"
        else:
            rec.approved_by = decided_by
            rec.approved_at = datetime.utcnow()
            rec.rejection_reason = rejection_reason or "Rejected by operational authority"
            audit_action = f"Human Rejected AI Recommendation: {rec.title}"

        # Persist audit record
        audit = SupplyChainAudit(
            business_id=business_id,
            timestamp=datetime.utcnow(),
            agent_name="Human Approval Gate",
            action=audit_action,
            reason=rec.rejection_reason if decision.upper() == "REJECTED" else "Executive verification and compliance sign-off",
            data_used={"recommendation_id": rec.id, "type": rec.recommendation_type, "cost": rec.expected_cost_usd},
            risk_level="Medium" if decision.upper() == "APPROVED" else "Low",
            approval_required=True,
            decision=decision.upper(),
            is_demo=rec.is_demo,
        )
        db.add(audit)
        db.commit()
        db.refresh(rec)

        return {
            "id": rec.id,
            "status": rec.approval_status,
            "approved_by": rec.approved_by,
            "decision": decision.upper(),
            "message": f"Successfully marked recommendation as {decision.upper()}.",
        }

    @staticmethod
    def get_audit_trail(db: Session, business_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch chronologically ordered audit events across all agents."""
        audits = db.query(SupplyChainAudit).filter(
            SupplyChainAudit.business_id == business_id
        ).order_by(SupplyChainAudit.timestamp.desc()).limit(limit).all()

        res = []
        for a in audits:
            res.append({
                "id": a.id,
                "timestamp": a.timestamp.strftime("%H:%M:%S UTC"),
                "date": a.timestamp.strftime("%Y-%m-%d"),
                "agent_name": a.agent_name,
                "action": a.action,
                "reason": a.reason,
                "data_used": a.data_used or {},
                "risk_level": a.risk_level,
                "approval_required": a.approval_required,
                "decision": a.decision,
            })
        return res
