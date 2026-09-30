from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.business import BusinessProfile
from app.services.proposal_service import ProposalService

router = APIRouter(prefix="/proposals", tags=["Action Proposals"])


def verify_business_ownership(db: Session, current_user: User, business_profile_id: str):
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
            detail="You do not have permission to access action proposals for this business profile"
        )
    return profile


@router.get("/{business_profile_id}")
def get_proposals(
    business_profile_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_business_ownership(db, current_user, business_profile_id)
    return ProposalService.get_proposals(db, business_profile_id)


@router.post("/{business_profile_id}")
def create_proposal(
    business_profile_id: str,
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_business_ownership(db, current_user, business_profile_id)
    return ProposalService.create_proposal(db, business_profile_id, data)


@router.post("/{business_profile_id}/{proposal_id}/confirm")
def confirm_proposal(
    business_profile_id: str,
    proposal_id: str,
    payload: Dict[str, Any] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_business_ownership(db, current_user, business_profile_id)
    confirmed_by = current_user.full_name or "Mohith K"
    if payload and payload.get("confirmed_by"):
        confirmed_by = payload["confirmed_by"]
    return ProposalService.confirm_proposal(
        db, business_profile_id, proposal_id, confirmed_by=confirmed_by
    )
