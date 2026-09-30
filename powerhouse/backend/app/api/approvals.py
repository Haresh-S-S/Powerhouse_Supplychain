from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status as http_status, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_optional_user
from app.models.user import User
from app.models.business import BusinessProfile
from app.schemas.approval import ApprovalResponse, ApprovalUpdate
from app.services.approval_service import ApprovalService

router = APIRouter(prefix="/approvals", tags=["Approvals & Licences"])


@router.get("", response_model=List[ApprovalResponse])
def list_approvals(
    business_profile_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    if business_profile_id and current_user:
        profile = db.query(BusinessProfile).filter(BusinessProfile.id == business_profile_id).first()
        if profile and profile.user_id and profile.user_id != current_user.id:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you do not have permission to view approvals for this profile.",
            )

    return ApprovalService.list_approvals(
        db,
        business_profile_id=business_profile_id,
        status=status,
        priority=priority,
        category=category,
        skip=skip,
        limit=limit,
    )


@router.get("/{id}", response_model=ApprovalResponse)
def get_approval(
    id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    approval = ApprovalService.get_approval(db, id)
    if not approval:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Approval with id '{id}' not found",
        )
    if current_user and approval.business_profile and approval.business_profile.user_id:
        if approval.business_profile.user_id != current_user.id:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you do not have permission to view this approval.",
            )
    return approval


@router.patch("/{id}", response_model=ApprovalResponse)
def update_approval(
    id: str,
    schema: ApprovalUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    approval = ApprovalService.get_approval(db, id)
    if not approval:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Approval with id '{id}' not found",
        )
    if current_user and approval.business_profile and approval.business_profile.user_id:
        if approval.business_profile.user_id != current_user.id:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you do not have permission to modify this approval.",
            )
    return ApprovalService.update_approval(db, id, schema)
