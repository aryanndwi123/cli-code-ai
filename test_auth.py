#!/usr/bin/env python3

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/auth"

def test_signup():
    """Test user signup"""
    print("=== Testing User Signup ===")

    signup_data = {
        "email": "test2@example.com",
        "password": "TestPass1!",
        "username": "testuser2"
    }

    try:
        response = requests.post(f"{BASE_URL}/signup", json=signup_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 201:
            print("✅ Signup successful!")
            return True
        else:
            print("❌ Signup failed!")
            return False

    except Exception as e:
        print(f"❌ Error during signup: {e}")
        return False

def test_signin():
    """Test user signin"""
    print("\n=== Testing User Signin ===")

    signin_data = {
        "email": "test2@example.com",
        "password": "TestPass1!"
    }

    try:
        response = requests.post(f"{BASE_URL}/signin", json=signin_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ Signin successful!")
            return response.json().get("access_token")
        else:
            print("❌ Signin failed!")
            return None

    except Exception as e:
        print(f"❌ Error during signin: {e}")
        return None

def test_profile(token):
    """Test getting user profile"""
    print("\n=== Testing Get Profile ===")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{BASE_URL}/profile", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ Profile retrieved successfully!")
            return True
        else:
            print("❌ Failed to get profile!")
            return False

    except Exception as e:
        print(f"❌ Error during profile retrieval: {e}")
        return False

def test_verify_token(token):
    """Test token verification"""
    print("\n=== Testing Token Verification ===")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{BASE_URL}/verify-token", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ Token verification successful!")
            return True
        else:
            print("❌ Token verification failed!")
            return False

    except Exception as e:
        print(f"❌ Error during token verification: {e}")
        return False

def test_refresh_api_key(token):
    """Test API key refresh"""
    print("\n=== Testing API Key Refresh ===")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(f"{BASE_URL}/refresh-api-key", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ API key refresh successful!")
            return True
        else:
            print("❌ API key refresh failed!")
            return False

    except Exception as e:
        print(f"❌ Error during API key refresh: {e}")
        return False

def test_logout(token):
    """Test user logout"""
    print("\n=== Testing User Logout ===")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(f"{BASE_URL}/logout", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ Logout successful!")
            return True
        else:
            print("❌ Logout failed!")
            return False

    except Exception as e:
        print(f"❌ Error during logout: {e}")
        return False

def test_invalid_credentials():
    """Test signin with invalid credentials"""
    print("\n=== Testing Invalid Credentials ===")

    signin_data = {
        "email": "test2@example.com",
        "password": "WrongPassword123!"
    }

    try:
        response = requests.post(f"{BASE_URL}/signin", json=signin_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 401:
            print("✅ Invalid credentials properly rejected!")
            return True
        else:
            print("❌ Invalid credentials test failed!")
            return False

    except Exception as e:
        print(f"❌ Error during invalid credentials test: {e}")
        return False

def test_unauthorized_access():
    """Test accessing protected endpoint without token"""
    print("\n=== Testing Unauthorized Access ===")

    try:
        response = requests.get(f"{BASE_URL}/profile")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 403:
            print("✅ Unauthorized access properly blocked!")
            return True
        else:
            print("❌ Unauthorized access test failed!")
            return False

    except Exception as e:
        print(f"❌ Error during unauthorized access test: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Testing Authentication System\n")

    # Test signup
    signup_success = test_signup()

    if not signup_success:
        print("\n❌ Signup failed, cannot continue with other tests")
        sys.exit(1)

    # Test signin
    token = test_signin()

    if not token:
        print("\n❌ Signin failed, cannot continue with authenticated tests")
        sys.exit(1)

    # Test authenticated endpoints
    test_profile(token)
    test_verify_token(token)
    test_refresh_api_key(token)

    # Test security features
    test_invalid_credentials()
    test_unauthorized_access()

    # Test logout
    test_logout(token)

    print("\n🎉 All authentication tests completed!")