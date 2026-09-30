from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.business import BusinessProfile
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    AuthStatusResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(schema: UserCreate, db: Session = Depends(get_db)):
    """Creates a new user account and returns an enterprise access token."""
    try:
        user = AuthService.register_user(db, schema)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    access_token = AuthService.create_access_token(data={"sub": user.id, "email": user.email})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
        onboarding_completed=False,
        active_business_id=None,
    )


@router.post("/login", response_model=TokenResponse)
def login(schema: UserLogin, db: Session = Depends(get_db)):
    """Authenticates existing user and returns an access token with onboarding status."""
    user = AuthService.authenticate_user(db, schema.email, schema.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify your credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = AuthService.create_access_token(data={"sub": user.id, "email": user.email})

    # Check canonical business profiles for this user
    profiles = (
        db.query(BusinessProfile)
        .filter(BusinessProfile.user_id == user.id)
        .order_by(BusinessProfile.updated_at.desc())
        .all()
    )

    onboarding_completed = False
    active_business_id = None

    if profiles:
        active_profile = profiles[0]
        active_business_id = active_profile.id
        onboarding_completed = bool(active_profile.onboarding_completed)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
        onboarding_completed=onboarding_completed,
        active_business_id=active_business_id,
    )


@router.get("/me", response_model=AuthStatusResponse)
def get_current_user_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns canonical authenticated user details, business profiles, and onboarding status."""
    profiles = (
        db.query(BusinessProfile)
        .filter(BusinessProfile.user_id == current_user.id)
        .order_by(BusinessProfile.updated_at.desc())
        .all()
    )

    business_profiles_data = []
    active_business = None
    onboarding_completed = False

    for p in profiles:
        p_dict = {
            "id": p.id,
            "business_name": p.business_name,
            "business_type": p.business_type,
            "business_category": p.business_category,
            "image_category": p.image_category,
            "city": p.city,
            "state": p.state,
            "onboarding_completed": p.onboarding_completed,
            "employee_count": p.employee_count,
            "annual_turnover": p.annual_turnover,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        business_profiles_data.append(p_dict)
        if p.onboarding_completed:
            onboarding_completed = True

    if business_profiles_data:
        active_business = business_profiles_data[0]

    return AuthStatusResponse(
        authenticated=True,
        user=UserResponse.model_validate(current_user),
        onboarding_completed=onboarding_completed,
        business_profiles=business_profiles_data,
        active_business=active_business,
    )


@router.post("/logout")
def logout():
    """Confirms session termination."""
    return {"message": "Successfully signed out from POWER HOUSE."}
