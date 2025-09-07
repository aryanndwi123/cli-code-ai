import os

class Config:
    """Configuration settings for basault"""
    
    # API Configuration
    API_BASE_URL = os.getenv('BASAULT_API_URL', 'https://cli-code-ai.vercel.app/api')
    
    # File paths
    TOKEN_FILE = os.path.expanduser('~/.basault-token')  # Store in user's home directory
    CONFIG_FILE = os.path.expanduser('~/.basault-config')
    
    # Request settings
    REQUEST_TIMEOUT = int(os.getenv('BASAULT_TIMEOUT', '30'))
    
    @classmethod
    def get_api_url(cls):
        """Get API URL with fallback"""
        return cls.API_BASE_URL
    
    @classmethod
    def set_api_url(cls, url):
        """Set API URL"""
        cls.API_BASE_URL = url
        # Save to config file
        import json
        config_data = {'api_url': url}
        try:
            with open(cls.CONFIG_FILE, 'w') as f:
                json.dump(config_data, f)
        except:
            pass