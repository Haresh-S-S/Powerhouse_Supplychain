from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate


class AlertService:
    @staticmethod
    def list_alerts(
        db: Session,
        business_profile_id: Optional[str] = None,
        is_read: Optional[bool] = None,
        severity: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Alert]:
        query = db.query(Alert)
        if business_profile_id:
            query = query.filter(Alert.business_profile_id == business_profile_id)
        if is_read is not None:
            query = query.filter(Alert.is_read == is_read)
        if severity:
            query = query.filter(Alert.severity == severity)
        return query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def create_alert(db: Session, schema: AlertCreate) -> Alert:
        alert = Alert(**schema.model_dump())
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def mark_as_read(db: Session, alert_id: str) -> Optional[Alert]:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        alert.is_read = True
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def mark_all_as_read(db: Session, business_profile_id: Optional[str] = None) -> int:
        query = db.query(Alert)
        if business_profile_id:
            query = query.filter(Alert.business_profile_id == business_profile_id)
        count = query.update({Alert.is_read: True})
        db.commit()
        return count
