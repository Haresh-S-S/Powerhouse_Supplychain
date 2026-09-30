from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.business import BusinessProfile
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit-logs", tags=["Audit Trail"])


@router.get("/{business_profile_id}")
def get_audit_trail(
    business_profile_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(BusinessProfile).filter(
        BusinessProfile.id == business_profile_id
    ).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found"
        )
    if profile.user_id and profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access audit records for this business profile"
        )
    logs = AuditService.get_audit_trail(db, business_profile_id)
    return [
        {
            "id": log.id,
            "business_profile_id": log.business_profile_id,
            "user_name": log.user_name,
            "action": log.action,
            "action_type": log.action,
            "action_name": log.target_entity_name,
            "action_status": "COMPLETED",
            "target_entity_type": log.target_entity_type,
            "target_entity_name": log.target_entity_name,
            "previous_state": log.previous_state,
            "new_state": log.new_state,
            "source": log.source,
            "proposal_id": log.proposal_id,
            "timestamp": log.timestamp.strftime("%d %b %Y, %I:%M %p") if log.timestamp else "",
            "details": log.details
        }
        for log in logs
    ]
