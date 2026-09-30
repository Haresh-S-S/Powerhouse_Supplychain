from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.approval import Approval
from app.schemas.approval import ApprovalCreate, ApprovalUpdate


class ApprovalService:
    @staticmethod
    def list_approvals(
        db: Session,
        business_profile_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Approval]:
        query = db.query(Approval)
        if business_profile_id:
            query = query.filter(Approval.business_profile_id == business_profile_id)
        if status:
            query = query.filter(Approval.status == status)
        if priority:
            query = query.filter(Approval.priority == priority)
        if category:
            query = query.filter(Approval.category == category)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_approval(db: Session, approval_id: str) -> Optional[Approval]:
        return db.query(Approval).filter(Approval.id == approval_id).first()

    @staticmethod
    def update_approval(db: Session, approval_id: str, schema: ApprovalUpdate) -> Optional[Approval]:
        approval = db.query(Approval).filter(Approval.id == approval_id).first()
        if not approval:
            return None
        for key, value in schema.model_dump(exclude_unset=True).items():
            setattr(approval, key, value)
        db.commit()
        db.refresh(approval)
        return approval
