from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.scheme import GovernmentScheme
from app.schemas.scheme import GovernmentSchemeCreate


class SchemeService:
    @staticmethod
    def list_schemes(
        db: Session,
        business_profile_id: Optional[str] = None,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[GovernmentScheme]:
        query = db.query(GovernmentScheme)
        if business_profile_id:
            query = query.filter(GovernmentScheme.business_profile_id == business_profile_id)
        if category:
            query = query.filter(GovernmentScheme.category == category)
        return query.order_by(GovernmentScheme.match_score.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_scheme(db: Session, scheme_id: str) -> Optional[GovernmentScheme]:
        return db.query(GovernmentScheme).filter(GovernmentScheme.id == scheme_id).first()

    @staticmethod
    def create_scheme(db: Session, schema: GovernmentSchemeCreate) -> GovernmentScheme:
        scheme = GovernmentScheme(**schema.model_dump())
        db.add(scheme)
        db.commit()
        db.refresh(scheme)
        return scheme
