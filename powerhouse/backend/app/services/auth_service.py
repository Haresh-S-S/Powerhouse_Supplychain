import os
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes a password using PBKDF2-HMAC-SHA256 with a random salt."""
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            100_000,
        )
        return f"{salt.hex()}${key.hex()}"

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies a plain password against the stored salt$hash."""
        try:
            salt_hex, hash_hex = hashed_password.split("$")
            salt = bytes.fromhex(salt_hex)
            key = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt,
                100_000,
            )
            return hmac.compare_digest(key.hex(), hash_hex)
        except Exception:
            return False

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Creates an enterprise HS256 JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
        """Decodes and validates an enterprise HS256 JWT access token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except (jwt.PyJWTError, Exception):
            return None

    @classmethod
    def get_user_by_email(cls, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower().strip()).first()

    @classmethod
    def get_user_by_id(cls, db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @classmethod
    def register_user(cls, db: Session, schema: UserCreate) -> User:
        """Registers a new user after verifying unique email."""
        clean_email = schema.email.lower().strip()
        existing = cls.get_user_by_email(db, clean_email)
        if existing:
            raise ValueError(f"An account with email '{clean_email}' already exists.")

        user = User(
            email=clean_email,
            hashed_password=cls.hash_password(schema.password),
            full_name=schema.full_name.strip(),
            phone_number=schema.phone_number.strip() if schema.phone_number else None,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @classmethod
    def authenticate_user(cls, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticates user credentials."""
        clean_email = email.lower().strip()
        user = cls.get_user_by_email(db, clean_email)
        if not user:
            return None
        if not cls.verify_password(password, user.hashed_password):
            return None
        return user
