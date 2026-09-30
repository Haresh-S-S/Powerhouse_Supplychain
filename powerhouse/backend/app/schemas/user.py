from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: str
    full_name: str
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    onboarding_completed: bool = False
    active_business_id: Optional[str] = None


class AuthStatusResponse(BaseModel):
    authenticated: bool
    user: Optional[UserResponse] = None
    onboarding_completed: bool = False
    business_profiles: List[dict] = []
    active_business: Optional[dict] = None
