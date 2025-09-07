

import requests
import json
import getpass
import os
import click
from datetime import datetime

# Configuration


class AuthClient:
   
    
    def __init__(self):
        self.api_url = os.getenv('API_BASE_URL', 'http://localhost:5000/api')
        self.token_file = os.getenv('TOKEN_FILE', '.auth_token')
        self.session = requests.Session()
        # Load existing token if available
        self._load_token()
    
    def _load_token(self):
        """Load authentication token from file"""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    token = data.get('token')
                    if token:
                        self.session.headers.update({'Authorization': f'Bearer {token}'})
            except:
                pass
    
    def _save_token(self, token):
        """Save authentication token to file"""
        with open(self.token_file, 'w') as f:
            json.dump({
                'token': token,
                'saved_at': datetime.now().isoformat()
            }, f)
        self.session.headers.update({'Authorization': f'Bearer {token}'})
    
    def _clear_token(self):
        """Clear authentication token"""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def signup(self, email, password):
        """Register new user via API"""
        try:
            response = self.session.post(f"{self.api_url}/signup", json={
                'email': email,
                'password': password
            })
            
            if response.status_code == 201:
                return True, "Account created successfully"
            elif response.status_code == 409:
                return False, "User already exists"
            else:
                error_msg = response.json().get('error', 'Signup failed')
                return False, error_msg
                
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def signin(self, email, password):
        """Sign in user via API"""
        try:
            response = self.session.post(f"{self.api_url}/signin", json={
                'email': email,
                'password': password
            })
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                if token:
                    self._save_token(token)
                    return True, "Login successful"
                return False, "No token received"
            elif response.status_code == 401:
                return False, "Invalid email or password"
            else:
                error_msg = response.json().get('error', 'Login failed')
                return False, error_msg
                
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def logout(self):
        """Logout user"""
        try:
            # Call server logout endpoint
            response = self.session.post(f"{self.api_url}/logout")
            
            # Clear local token regardless of server response
            self._clear_token()
            
            if response.status_code == 200:
                return True, "Logged out successfully"
            else:
                return True, "Logged out locally"
                
        except requests.exceptions.ConnectionError:
            # Clear local token even if server is unreachable
            self._clear_token()
            return True, "Logged out locally (server unreachable)"
        except Exception as e:
            self._clear_token()
            return True, f"Logged out locally ({str(e)})"
    
    def get_profile(self):
        """Get user profile via API"""
        try:
            response = self.session.get(f"{self.api_url}/profile")
            
            if response.status_code == 200:
                return True, response.json()
            elif response.status_code == 401:
                return False, "Not authenticated"
            else:
                return False, "Failed to get profile"
                
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def is_logged_in(self):
        """Check if user is logged in"""
        success, data = self.get_profile()
        return success

# Initialize auth client
auth = AuthClient()

@click.group()
def cli():
    
    pass

@cli.command()
def signup():
    """Register a new account"""
    print("=== Sign Up ===")
    
    email = input("Email: ").strip()
    if not email:
        print("Email cannot be empty")
        return
    
    password = getpass.getpass("Password: ")
    if not password:
        print("Password cannot be empty")
        return
    
    confirm_password = getpass.getpass("Confirm Password: ")
    if password != confirm_password:
        print("Passwords don't match")
        return
    
    print("⏳ Creating account...")
    success, message = auth.signup(email, password)
    if success:
        print(f"Success: {message}")
    else:
        print(f"Error: {message}")

@cli.command()
def signin():
    """Sign into your account"""
    print("=== Sign In ===")
    
    # Check if already logged in
    if auth.is_logged_in():
        success, profile = auth.get_profile()
        if success:
            print(f"Already logged in as {profile['email']}")
            return
    
    email = input("Email: ").strip()
    if not email:
        print("Email cannot be empty")
        return
    
    password = getpass.getpass("Password: ")
    if not password:
        print("Password cannot be empty")
        return
    
    print("⏳ Signing in...")
    success, message = auth.signin(email, password)
    if success:
        print(f"Success: {message}")
    else:
        print(f"Error: {message}")

@cli.command()
def logout():
    """Log out of your account"""
    print("=== Logout ===")
    
    success, message = auth.logout()
    if success:
        print(f"Success: {message}")
    else:
        print(f"Error: {message}")

@cli.command()
def status():
    """Check login status"""
    print("⏳ Checking status...")
    success, data = auth.get_profile()
    if success:
        print(f" Logged in as: {data['email']}")
        print(f" Member since: {data['created_at']}")
    else:
        print(f" Not logged in ({data})")

@cli.command()
def protected():
    """Example protected command"""
    print("⏳ Checking authentication...")
    success, data = auth.get_profile()
    if not success:
        print("basault Please sign in first")
        print("Run: python cli_client.py signin")
        return
    
    print(f"🔒 Welcome to protected area, {data['email']}!")
    print(f"🎉 You have access to premium features!")

if __name__ == '__main__':
    cli()

