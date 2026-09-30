from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


class AuditService:
    @staticmethod
    def get_audit_trail(db: Session, business_profile_id: str) -> List[AuditLog]:
        return db.query(AuditLog).filter(
            AuditLog.business_profile_id == business_profile_id
        ).order_by(AuditLog.timestamp.desc()).all()
