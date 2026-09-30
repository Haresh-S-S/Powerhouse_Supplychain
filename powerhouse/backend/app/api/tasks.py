from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status as http_status, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_optional_user
from app.models.user import User
from app.models.business import BusinessProfile
from app.schemas.compliance_task import (
    ComplianceTaskCreate,
    ComplianceTaskUpdate,
    ComplianceTaskResponse,
)
from app.services.task_service import ComplianceTaskService

router = APIRouter(prefix="/tasks", tags=["Compliance Tasks"])


@router.get("", response_model=List[ComplianceTaskResponse])
def list_tasks(
    business_profile_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
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
                detail="Access forbidden: you do not have permission to view tasks for this profile.",
            )

    return ComplianceTaskService.list_tasks(
        db,
        business_profile_id=business_profile_id,
        status=status,
        priority=priority,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=ComplianceTaskResponse, status_code=http_status.HTTP_201_CREATED)
def create_task(
    schema: ComplianceTaskCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    if current_user and schema.business_profile_id:
        profile = db.query(BusinessProfile).filter(BusinessProfile.id == schema.business_profile_id).first()
        if profile and profile.user_id and profile.user_id != current_user.id:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you do not have permission to create tasks for this profile.",
            )
    return ComplianceTaskService.create_task(db, schema)


@router.get("/{id}", response_model=ComplianceTaskResponse)
def get_task(
    id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    task = ComplianceTaskService.get_task(db, id)
    if not task:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{id}' not found",
        )
    if current_user and task.business_profile and task.business_profile.user_id:
        if task.business_profile.user_id != current_user.id:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you do not have permission to view this task.",
            )
    return task


@router.patch("/{id}", response_model=ComplianceTaskResponse)
def update_task(
    id: str,
    schema: ComplianceTaskUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    task = ComplianceTaskService.get_task(db, id)
    if not task:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{id}' not found",
        )
    if current_user and task.business_profile and task.business_profile.user_id:
        if task.business_profile.user_id != current_user.id:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you do not have permission to modify this task.",
            )
    return ComplianceTaskService.update_task(db, id, schema)


@router.patch("/{id}/complete", response_model=ComplianceTaskResponse)
def complete_task(
    id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    task = ComplianceTaskService.get_task(db, id)
    if not task:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{id}' not found",
        )
    if current_user and task.business_profile and task.business_profile.user_id:
        if task.business_profile.user_id != current_user.id:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you do not have permission to complete this task.",
            )
    return ComplianceTaskService.complete_task(db, id)
