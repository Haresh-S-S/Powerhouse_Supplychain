from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
)
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("", response_model=List[ApplicationResponse])
def list_applications(
    business_profile_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return ApplicationService.list_applications(
        db,
        business_profile_id=business_profile_id,
        status=status,
        department=department,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    schema: ApplicationCreate,
    db: Session = Depends(get_db),
):
    return ApplicationService.create_application(db, schema)


@router.get("/{id}", response_model=ApplicationResponse)
def get_application(
    id: str,
    db: Session = Depends(get_db),
):
    app = ApplicationService.get_application(db, id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id '{id}' not found",
        )
    return app


@router.patch("/{id}", response_model=ApplicationResponse)
def update_application(
    id: str,
    schema: ApplicationUpdate,
    db: Session = Depends(get_db),
):
    app = ApplicationService.update_application(db, id, schema)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id '{id}' not found",
        )
    return app
