#!/usr/bin/env python3

import requests
import json

BASE_URL = "http://localhost:8000/api/auth"

def delete_test_user():
    """Delete the test user"""
    print("=== Deleting Test User ===")

    # First sign in to get token
    signin_data = {
        "email": "test2@example.com",
        "password": "TestPass1!"
    }

    try:
        # Sign in
        print("Signing in...")
        response = requests.post(f"{BASE_URL}/signin", json=signin_data)

        if response.status_code != 200:
            print(f"❌ Failed to sign in: {response.json()}")
            return False

        token = response.json()["access_token"]
        print("✅ Signed in successfully")

        # Delete account
        print("Deleting account...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(f"{BASE_URL}/delete", headers=headers)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ Account deleted successfully!")
            return True
        else:
            print("❌ Failed to delete account!")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    delete_test_user()