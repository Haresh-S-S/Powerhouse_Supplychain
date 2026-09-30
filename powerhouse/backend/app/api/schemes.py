from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.schemas.scheme import (
    GovernmentSchemeCreate,
    GovernmentSchemeResponse,
)
from app.services.scheme_service import SchemeService

router = APIRouter(prefix="/schemes", tags=["Government Schemes"])


@router.get("", response_model=List[GovernmentSchemeResponse])
def list_schemes(
    business_profile_id: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return SchemeService.list_schemes(
        db,
        business_profile_id=business_profile_id,
        category=category,
        skip=skip,
        limit=limit,
    )


@router.get("/{id}", response_model=GovernmentSchemeResponse)
def get_scheme(
    id: str,
    db: Session = Depends(get_db),
):
    scheme = SchemeService.get_scheme(db, id)
    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme with id '{id}' not found",
        )
    return scheme
