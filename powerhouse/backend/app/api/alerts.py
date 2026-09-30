from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.schemas.alert import (
    AlertCreate,
    AlertResponse,
)
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts & Notifications"])


@router.get("", response_model=List[AlertResponse])
def list_alerts(
    business_profile_id: Optional[str] = Query(None),
    is_read: Optional[bool] = Query(None),
    severity: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return AlertService.list_alerts(
        db,
        business_profile_id=business_profile_id,
        is_read=is_read,
        severity=severity,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(
    schema: AlertCreate,
    db: Session = Depends(get_db),
):
    return AlertService.create_alert(db, schema)


@router.patch("/{id}/read", response_model=AlertResponse)
def mark_alert_as_read(
    id: str,
    db: Session = Depends(get_db),
):
    alert = AlertService.mark_as_read(db, id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id '{id}' not found",
        )
    return alert


@router.patch("/read-all", response_model=dict)
def mark_all_alerts_as_read(
    business_profile_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    count = AlertService.mark_all_as_read(db, business_profile_id=business_profile_id)
    return {"status": "success", "updated_count": count}
