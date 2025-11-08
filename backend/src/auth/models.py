from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

Base = declarative_base()


class User(Base):
    """User model for database"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    api_key = Column(String, unique=True, nullable=True)


class UserCreate(BaseModel):
    """Pydantic model for user creation"""
    email: EmailStr
    password: str
    username: Optional[str] = None


class UserLogin(BaseModel):
    """Pydantic model for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Pydantic model for user response"""
    id: int
    email: str
    username: Optional[str]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    """Token data for validation"""
    user_id: Optional[int] = None
    email: Optional[str] = None