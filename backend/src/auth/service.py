import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .models import User, UserCreate, UserLogin, TokenData
from ..core.database import get_db
from ..core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters long"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if not (has_upper and has_lower):
        return False, "Password must contain both uppercase and lowercase letters"
    
    if not has_digit:
        return False, "Password must contain at least one digit"
    
    if not has_special:
        return False, "Password must contain at least one special character"
    
    return True, ""


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
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id_str = payload.get("sub")
            email: str = payload.get("email")

            if user_id_str is None:
                return None

            try:
                user_id = int(user_id_str)
            except (ValueError, TypeError):
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
        is_valid, error_msg = validate_password_strength(user.password)
        if not is_valid:
            raise ValueError(error_msg)
        
        if self.get_user_by_email(db, user.email):
            raise ValueError("User with this email already exists")
        
        if user.username:
            existing_user = db.query(User).filter(User.username == user.username).first()
            if existing_user:
                raise ValueError("Username already taken")

        hashed_password = self.get_password_hash(user.password)

        api_key = self.generate_api_key()

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

        user.last_login = datetime.now(timezone.utc)
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