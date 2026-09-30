from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.business import BusinessProfile
from app.models.action_proposal import ActionProposal
from app.models.audit_log import AuditLog
from app.services.analysis_service import BusinessAnalysisService

router = APIRouter(prefix="/demo", tags=["Demo State Management"])


@router.post("/reset/{business_profile_id}")
def reset_demo_state(
    business_profile_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Safely resets the demonstration business profile and regenerates clean baseline state.
    Strictly isolated to the authenticated user's business profile; never deletes real user accounts.
    """
    profile = db.query(BusinessProfile).filter(
        BusinessProfile.id == business_profile_id
    ).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business profile not found")
    if profile.user_id and profile.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    # Clear proposals and transient logs for this profile
    db.query(ActionProposal).filter(ActionProposal.business_profile_id == business_profile_id).delete()
    db.query(AuditLog).filter(AuditLog.business_profile_id == business_profile_id).delete()
    db.commit()

    # Re-run clean baseline analysis
    analysis = BusinessAnalysisService.run_and_save_analysis(db, business_profile_id)
    return {
        "success": True,
        "message": "Demo workspace successfully reset to pristine baseline state.",
        "business_profile_id": business_profile_id,
        "analysis_id": analysis.id if analysis else None
    }
