from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.compliance_task import ComplianceTask
from app.schemas.compliance_task import ComplianceTaskCreate, ComplianceTaskUpdate


class ComplianceTaskService:
    @staticmethod
    def list_tasks(
        db: Session,
        business_profile_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ComplianceTask]:
        query = db.query(ComplianceTask)
        if business_profile_id:
            query = query.filter(ComplianceTask.business_profile_id == business_profile_id)
        if status:
            query = query.filter(ComplianceTask.status == status)
        if priority:
            query = query.filter(ComplianceTask.priority == priority)
        return query.order_by(ComplianceTask.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_task(db: Session, task_id: str) -> Optional[ComplianceTask]:
        return db.query(ComplianceTask).filter(ComplianceTask.id == task_id).first()

    @staticmethod
    def create_task(db: Session, schema: ComplianceTaskCreate) -> ComplianceTask:
        task = ComplianceTask(**schema.model_dump())
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update_task(db: Session, task_id: str, schema: ComplianceTaskUpdate) -> Optional[ComplianceTask]:
        task = db.query(ComplianceTask).filter(ComplianceTask.id == task_id).first()
        if not task:
            return None
        for key, value in schema.model_dump(exclude_unset=True).items():
            setattr(task, key, value)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def complete_task(db: Session, task_id: str) -> Optional[ComplianceTask]:
        task = db.query(ComplianceTask).filter(ComplianceTask.id == task_id).first()
        if not task:
            return None
        task.status = "Completed"
        task.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        return task
