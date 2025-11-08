from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from .models import UserCreate, UserLogin, UserResponse, Token
from .service import auth_service
from ..core.database import get_db
from ..core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        db_user = auth_service.create_user(db, user)
        return UserResponse.from_orm(db_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post("/signin", response_model=Token)
async def signin(user_login: UserLogin, db: Session = Depends(get_db)):
    """Sign in user and return access token"""
    user = auth_service.authenticate_user(db, user_login.email, user_login.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )

    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": auth_service.access_token_expire_minutes * 60
    }


@router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """Logout user (client should discard token)"""
    # In a stateless JWT system, logout is handled client-side
    # For additional security, you could maintain a blacklist of tokens
    return {"message": "Successfully logged out"}


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: UserResponse = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


@router.post("/refresh-api-key")
async def refresh_api_key(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh user's API key"""
    try:
        new_api_key = auth_service.revoke_api_key(db, current_user.id)
        return {"api_key": new_api_key, "message": "API key refreshed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/verify-token")
async def verify_token(current_user: UserResponse = Depends(get_current_user)):
    """Verify if token is valid"""
    return {"valid": True, "user": current_user}


@router.post("/deactivate")
async def deactivate_account(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate current user account"""
    success = auth_service.deactivate_user(db, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"message": "Account deactivated successfully"}