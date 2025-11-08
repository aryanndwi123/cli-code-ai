import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .models import User, UserCreate, UserLogin, TokenData
from ..core.database import get_db
from ..core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service with improved security"""

    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: int = payload.get("sub")
            email: str = payload.get("email")

            if user_id is None:
                return None

            return TokenData(user_id=user_id, email=email)
        except jwt.PyJWTError:
            return None

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    def create_user(self, db: Session, user: UserCreate) -> User:
        """Create new user"""
        # Check if user already exists
        if self.get_user_by_email(db, user.email):
            raise ValueError("User with this email already exists")

        # Hash password
        hashed_password = self.get_password_hash(user.password)

        # Generate API key
        api_key = self.generate_api_key()

        # Create user
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            api_key=api_key
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.get_user_by_email(db, email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        return user

    def authenticate_api_key(self, db: Session, api_key: str) -> Optional[User]:
        """Authenticate user with API key"""
        return db.query(User).filter(User.api_key == api_key, User.is_active == True).first()

    def revoke_api_key(self, db: Session, user_id: int) -> str:
        """Revoke current API key and generate new one"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        new_api_key = self.generate_api_key()
        user.api_key = new_api_key
        db.commit()
        return new_api_key

    def deactivate_user(self, db: Session, user_id: int) -> bool:
        """Deactivate user account"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            return False

        user.is_active = False
        db.commit()
        return True


# Global auth service instance
auth_service = AuthService()