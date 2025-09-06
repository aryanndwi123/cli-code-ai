import requests
import json
import os
from datetime import datetime
from .config import Config

class AuthClient:
    """Authentication client for API communication"""
    
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        self.session.timeout = self.config.REQUEST_TIMEOUT
        self._load_token()
    
    def _load_token(self):
        """Load authentication token from file"""
        if os.path.exists(self.config.TOKEN_FILE):
            try:
                with open(self.config.TOKEN_FILE, 'r') as f:
                    data = json.load(f)
                    token = data.get('token')
                    if token:
                        self.session.headers.update({'Authorization': f'Bearer {token}'})
            except:
                pass
    
    def _save_token(self, token):
        """Save authentication token to file"""
        os.makedirs(os.path.dirname(self.config.TOKEN_FILE), exist_ok=True)
        with open(self.config.TOKEN_FILE, 'w') as f:
            json.dump({
                'token': token,
                'saved_at': datetime.now().isoformat()
            }, f)
        self.session.headers.update({'Authorization': f'Bearer {token}'})
    
    def _clear_token(self):
        """Clear authentication token"""
        if os.path.exists(self.config.TOKEN_FILE):
            os.remove(self.config.TOKEN_FILE)
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def signup(self, email, password):
        """Register new user"""
        try:
            response = self.session.post(f"{self.config.get_api_url()}/signup", json={
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
        """Sign in user"""
        try:
            response = self.session.post(f"{self.config.get_api_url()}/signin", json={
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
            response = self.session.post(f"{self.config.get_api_url()}/logout")
            self._clear_token()
            
            if response.status_code == 200:
                return True, "Logged out successfully"
            else:
                return True, "Logged out locally"
                
        except requests.exceptions.ConnectionError:
            self._clear_token()
            return True, "Logged out locally (server unreachable)"
        except Exception as e:
            self._clear_token()
            return True, f"Logged out locally ({str(e)})"
    
    def get_profile(self):
        """Get user profile"""
        try:
            response = self.session.get(f"{self.config.get_api_url()}/profile")
            
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