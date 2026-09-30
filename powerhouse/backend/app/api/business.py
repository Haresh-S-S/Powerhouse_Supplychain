from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_optional_user, get_current_user
from app.models.user import User
from app.models.business import BusinessProfile
from app.schemas.business import (
    BusinessProfileCreate,
    BusinessProfileUpdate,
    BusinessProfileResponse,
)
from app.services.business_service import BusinessProfileService

router = APIRouter(prefix="/business-profile", tags=["Business Profile"])


@router.post("", response_model=BusinessProfileResponse, status_code=status.HTTP_201_CREATED)
def create_business_profile(
    schema: BusinessProfileCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    if current_user and not schema.user_id:
        schema.user_id = current_user.id
    return BusinessProfileService.create_profile(db, schema)


@router.get("/user/me", response_model=List[BusinessProfileResponse])
def get_my_business_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns all canonical business profiles belonging to the authenticated user."""
    return (
        db.query(BusinessProfile)
        .filter(BusinessProfile.user_id == current_user.id)
        .order_by(BusinessProfile.updated_at.desc())
        .all()
    )


@router.get("", response_model=List[BusinessProfileResponse])
def list_business_profiles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    if current_user:
        user_profiles = (
            db.query(BusinessProfile)
            .filter(BusinessProfile.user_id == current_user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        if user_profiles:
            return user_profiles
    return BusinessProfileService.list_profiles(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=BusinessProfileResponse)
def get_business_profile(
    id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    profile = BusinessProfileService.get_profile(db, id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business profile with id '{id}' not found",
        )
    # Multi-tenant isolation enforcement
    if current_user and profile.user_id and profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to access this business profile.",
        )
    return profile


@router.put("/{id}", response_model=BusinessProfileResponse)
def update_business_profile(
    id: str,
    schema: BusinessProfileUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    profile = BusinessProfileService.get_profile(db, id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business profile with id '{id}' not found",
        )
    # Multi-tenant isolation enforcement
    if current_user and profile.user_id and profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to modify this business profile.",
        )
    return BusinessProfileService.update_profile(db, id, schema)
