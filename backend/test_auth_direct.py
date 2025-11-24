#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.auth.service import auth_service
from src.auth.models import UserCreate
from src.core.database import SessionLocal, create_tables
import traceback

def test_auth_service_direct():
    """Test auth service directly without HTTP layer"""
    print("🔍 Testing Auth Service Direct\n")

    # Initialize database
    print("1. Initializing database...")
    try:
        create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        traceback.print_exc()
        return False

    # Test user creation
    print("\n2. Testing user creation...")
    db = SessionLocal()
    try:
        user_data = UserCreate(
            email="test@example.com",
            password="TestPass1!",
            username="testuser"
        )

        # Check if user already exists
        existing_user = auth_service.get_user_by_email(db, user_data.email)
        if existing_user:
            print(f"⚠ User with email {user_data.email} already exists, using existing user")
            user = existing_user
        else:
            user = auth_service.create_user(db, user_data)
            print("✅ User created successfully")
            print(f"   User ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Username: {user.username}")
            print(f"   API Key: {user.api_key[:10]}...")

    except Exception as e:
        print(f"❌ User creation failed: {e}")
        traceback.print_exc()
        db.close()
        return False

    # Test authentication
    print("\n3. Testing authentication...")
    try:
        authenticated_user = auth_service.authenticate_user(
            db, user_data.email, user_data.password
        )
        if authenticated_user:
            print("✅ User authentication successful")
            print(f"   Authenticated user: {authenticated_user.email}")
        else:
            print("❌ User authentication failed")
            db.close()
            return False
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        traceback.print_exc()
        db.close()
        return False

    # Test token creation
    print("\n4. Testing token creation...")
    try:
        token = auth_service.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        print("✅ Token created successfully")
        print(f"   Token (first 20 chars): {token[:20]}...")
    except Exception as e:
        print(f"❌ Token creation failed: {e}")
        traceback.print_exc()
        db.close()
        return False

    # Test token verification
    print("\n5. Testing token verification...")
    try:
        token_data = auth_service.verify_token(token)
        if token_data and token_data.user_id == user.id:
            print("✅ Token verification successful")
            print(f"   Verified user ID: {token_data.user_id}")
        else:
            print("❌ Token verification failed")
            db.close()
            return False
    except Exception as e:
        print(f"❌ Token verification test failed: {e}")
        traceback.print_exc()
        db.close()
        return False

    # Test API key authentication
    print("\n6. Testing API key authentication...")
    try:
        api_authenticated_user = auth_service.authenticate_api_key(db, user.api_key)
        if api_authenticated_user and api_authenticated_user.id == user.id:
            print("✅ API key authentication successful")
            print(f"   API authenticated user: {api_authenticated_user.email}")
        else:
            print("❌ API key authentication failed")
            db.close()
            return False
    except Exception as e:
        print(f"❌ API key authentication test failed: {e}")
        traceback.print_exc()
        db.close()
        return False

    db.close()
    print("\n🎉 All direct auth service tests passed!")
    return True

if __name__ == "__main__":
    test_auth_service_direct()