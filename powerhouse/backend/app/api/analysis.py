from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_optional_user
from app.models.user import User
from app.schemas.analysis import BusinessAnalysisResponse
from app.services.analysis_service import BusinessAnalysisService
from app.services.business_service import BusinessProfileService

router = APIRouter(prefix="/business-analysis", tags=["Business Analysis"])


@router.post("/{business_profile_id}", response_model=BusinessAnalysisResponse, status_code=status.HTTP_201_CREATED)
def run_business_analysis(
    business_profile_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    profile = BusinessProfileService.get_profile(db, business_profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business profile with id '{business_profile_id}' not found",
        )
    if current_user and profile.user_id and profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to trigger analysis on this business profile.",
        )
    analysis = BusinessAnalysisService.run_and_save_analysis(db, business_profile_id)
    return analysis


@router.get("/{business_profile_id}/latest", response_model=BusinessAnalysisResponse)
def get_latest_analysis(
    business_profile_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    profile = BusinessProfileService.get_profile(db, business_profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business profile with id '{business_profile_id}' not found",
        )
    if current_user and profile.user_id and profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to access analysis for this business profile.",
        )
    analysis = BusinessAnalysisService.get_latest_for_profile(db, business_profile_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No analysis found for business profile id '{business_profile_id}'",
        )
    return analysis


@router.get("/report/{analysis_id}", response_model=BusinessAnalysisResponse)
def get_analysis_by_id(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    analysis = BusinessAnalysisService.get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business analysis with id '{analysis_id}' not found",
        )
    profile = BusinessProfileService.get_profile(db, analysis.business_profile_id)
    if profile and current_user and profile.user_id and profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to access this analysis report.",
        )
    return analysis
