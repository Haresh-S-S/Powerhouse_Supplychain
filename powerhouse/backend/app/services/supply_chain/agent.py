from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.supplier import Supplier, SupplyItem, SupplyChainRisk
from app.models.action_proposal import ActionProposal
from app.services.supply_chain.risk_service import SupplyChainRiskService
from app.services.proposal_service import ProposalService


class SupplyChainAgent:
    """
    Governed AI Agent for Supply Chain Resilience.
    Executes the 8-stage intelligence pattern:
    Observe -> Retrieve -> Detect -> Analyze -> Reason -> Recommend -> Validate -> ActionProposal.
    Strictly prevents unapproved external contact or automatic vendor modifications.
    """

    @classmethod
    def analyze_business_supply_chain(cls, db: Session, business_id: str) -> Dict[str, Any]:
        # 1. OBSERVE & RETRIEVE
        suppliers = db.query(Supplier).filter(Supplier.business_id == business_id).all()
        items = db.query(SupplyItem).filter(SupplyItem.business_id == business_id).all()

        # 2. DETECT
        detected_risks = SupplyChainRiskService.detect_and_sync_risks(db, business_id)

        # 3. ANALYZE & REASON
        score_data = SupplyChainRiskService.calculate_resilience_score(db, business_id)

        # 4. RECOMMEND
        recommendations = []
        for risk in detected_risks:
            recommendations.append({
                "risk_id": risk.id,
                "title": risk.title,
                "priority": risk.priority,
                "recommended_action": risk.recommended_action,
                "estimated_risk_reduction": f"{risk.estimated_risk_reduction}%",
                "evidence_summary": f"Detected in {risk.category} for {risk.supplier.name if risk.supplier else 'Inventory'}"
            })

        return {
            "status": "COMPLETED",
            "business_id": business_id,
            "suppliers_analyzed": len(suppliers),
            "items_analyzed": len(items),
            "risks_detected": len(detected_risks),
            "resilience_score": score_data["score"],
            "resilience_rating": score_data["rating"],
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }

    @classmethod
    def propose_action_for_risk(cls, db: Session, business_id: str, risk_id: str) -> ActionProposal:
        """
        Transforms a validated supply-chain risk recommendation into an official ActionProposal.
        Human approval is strictly required before any task or procurement action is created.
        """
        risk = db.query(SupplyChainRisk).filter(
            SupplyChainRisk.id == risk_id,
            SupplyChainRisk.business_id == business_id
        ).first()

        if not risk:
            raise ValueError("Supply chain risk not found or does not belong to active business.")

        # Ensure policy check passes
        if risk.policy_check_status == "BLOCK":
            raise ValueError("Action Proposal blocked by policy guardrails.")

        proposal_data = {
            "action_type": "SUPPLY_CHAIN_RESILIENCE_ACTION",
            "title": f"Execute Resilience Action: {risk.title}",
            "reason": f"Supply Chain Agent identified operational vulnerability in {risk.category}. {risk.issue}",
            "affected_entity_type": "supply_chain_risk",
            "affected_entity_id": risk.id,
            "changes": {
                "status": {"from": risk.status, "to": "ACTION_CREATED"},
                "risk_id": risk.id,
                "recommended_action": risk.recommended_action,
                "estimated_risk_reduction": f"{risk.estimated_risk_reduction}%",
                "evidence": risk.evidence,
            },
            "risk_level": "Medium" if risk.priority in ["Critical", "High"] else "Low",
            "created_by": "Supply Chain Resilience Agent"
        }

        proposal = ProposalService.create_proposal(db, business_id, proposal_data)
        risk.status = "AWAITING_APPROVAL"
        risk.updated_at = datetime.utcnow()
        db.commit()

        return proposal
