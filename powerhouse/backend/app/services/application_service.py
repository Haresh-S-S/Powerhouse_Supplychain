from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationUpdate


class ApplicationService:
    @staticmethod
    def list_applications(
        db: Session,
        business_profile_id: Optional[str] = None,
        status: Optional[str] = None,
        department: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Application]:
        query = db.query(Application)
        if business_profile_id:
            query = query.filter(Application.business_profile_id == business_profile_id)
        if status:
            query = query.filter(Application.status == status)
        if department:
            query = query.filter(Application.department == department)
        return query.order_by(Application.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_application(db: Session, app_id: str) -> Optional[Application]:
        return db.query(Application).filter(Application.id == app_id).first()

    @staticmethod
    def create_application(db: Session, schema: ApplicationCreate) -> Application:
        application = Application(**schema.model_dump())
        db.add(application)
        db.commit()
        db.refresh(application)
        return application

    @staticmethod
    def update_application(db: Session, app_id: str, schema: ApplicationUpdate) -> Optional[Application]:
        application = db.query(Application).filter(Application.id == app_id).first()
        if not application:
            return None
        for key, value in schema.model_dump(exclude_unset=True).items():
            setattr(application, key, value)
        db.commit()
        db.refresh(application)
        return application
