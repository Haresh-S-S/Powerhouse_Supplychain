from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.business import BusinessProfile
from app.schemas.business import BusinessProfileCreate, BusinessProfileUpdate


class BusinessProfileService:
    @staticmethod
    def get_profile(db: Session, profile_id: str) -> Optional[BusinessProfile]:
        return db.query(BusinessProfile).filter(BusinessProfile.id == profile_id).first()

    @staticmethod
    def get_first_or_default(db: Session) -> Optional[BusinessProfile]:
        return db.query(BusinessProfile).first()

    @staticmethod
    def list_profiles(db: Session, skip: int = 0, limit: int = 100) -> List[BusinessProfile]:
        return db.query(BusinessProfile).offset(skip).limit(limit).all()

    @staticmethod
    def create_profile(db: Session, schema: BusinessProfileCreate) -> BusinessProfile:
        profile = BusinessProfile(**schema.model_dump())
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def update_profile(db: Session, profile_id: str, schema: BusinessProfileUpdate) -> Optional[BusinessProfile]:
        profile = db.query(BusinessProfile).filter(BusinessProfile.id == profile_id).first()
        if not profile:
            return None

        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(profile, key, value)

        db.commit()
        db.refresh(profile)
        return profile
