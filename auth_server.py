
from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras
import hashlib
import jwt
import os
import ssl
from datetime import datetime, timedelta
from functools import wraps
from urllib.parse import urlparse

app = Flask(__name__)

# Configuration - Replace with your hosted PostgreSQL URL
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')



DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:321nnayra@db.bpbmptdvsxcermkatxoc.supabase.co:5432/postgres')

def get_db():
    """Get PostgreSQL database connection"""
    try:
        # Parse the database URL
        url = urlparse(DATABASE_URL)
        
        conn_params = {
            'host': url.hostname,
            'port': url.port or 5432,
            'database': url.path[1:], 
            'user': url.username,
            'password': url.password,
            'sslmode': 'require',
            'sslcert': None,
            'sslkey': None,
            'sslrootcert': None,
            'connect_timeout': 10,
            'options': '-c default_transaction_isolation=read_committed'
        }
        if hasattr(ssl, 'create_default_context'):
            conn_params['sslcontext'] = ssl.create_default_context()
        
        print(f"Connecting to database: {url.hostname}:{url.port}")
        conn = psycopg2.connect(**conn_params)
        
        # Test the connection
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        cursor.close()
        
        print("Database connection successful")
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise

def init_db():
    """Initialize PostgreSQL database"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index for faster email lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Database initialized successfully")
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"Database connection failed: {error_msg}")
        
        # Provide specific error guidance
        if "Network is unreachable" in error_msg:
            print("This is likely an IPv6/network connectivity issue between Render and Supabase")
            print("Possible solutions:")
            print("1. Check Supabase network settings")
            print("2. Verify database URL is correct")
            print("3. Try alternative connection methods")
        
        raise
    except Exception as e:
        print(f"Unexpected database error: {e}")
        raise

def hash_password(password):
    """Hash password with SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(user_id, email):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated

@app.route('/api/signup', methods=['POST'])
def signup():
    """Register new user"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email'].strip().lower()
    password = data['password']
    
    
    if '@' not in email:
        return jsonify({'error': 'Invalid email format'}), 400
    
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': 'User already exists'}), 409
        
        # Create new user
        password_hash = hash_password(password)
        cursor.execute(
            'INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id',
            (email, password_hash)
        )
        
        user_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"New user created: {email} (ID: {user_id})")
        return jsonify({'message': 'User created successfully'}), 201
        
    except psycopg2.IntegrityError:
        return jsonify({'error': 'User already exists'}), 409
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/signin', methods=['POST'])
def signin():
    """Sign in user"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email'].strip().lower()
    password = data['password']
    
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Find user
        cursor.execute(
            'SELECT id, email, password_hash FROM users WHERE email = %s',
            (email,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user or user['password_hash'] != hash_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token
        token = generate_token(user['id'], user['email'])
        
        print(f"User signed in: {email}")
        return jsonify({
            'token': token,
            'message': 'Login successful'
        }), 200
        
    except Exception as e:
        print(f"Signin error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/logout', methods=['POST'])
@require_auth
def logout():
    """Logout user"""
    #Are we actually logging out or not?
    email = request.user.get('email')
    print(f"User logged out: {email}")
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/profile', methods=['GET'])
@require_auth
def profile():
    """Get user profile"""
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute(
            'SELECT email, created_at FROM users WHERE id = %s',
            (request.user['user_id'],)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'email': user['email'],
            'created_at': user['created_at'].isoformat()
        }), 200
        
    except Exception as e:
        print(f"Profile error: {e}")
        return jsonify({'error': 'Failed to get profile'}), 500

@app.route('/api/users', methods=['GET'])
@require_auth
def list_users():
    """List all users (admin endpoint)"""
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute('SELECT id, email, created_at FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        user_list = []
        for user in users:
            user_list.append({
                'id': user['id'],
                'email': user['email'],
                'created_at': user['created_at'].isoformat()
            })
        
        return jsonify({
            'users': user_list,
            'total': len(user_list)
        }), 200
        
    except Exception as e:
        print(f"List users error: {e}")
        return jsonify({'error': 'Failed to list users'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint with database connectivity"""
    try:
        # Test database connection
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'users_count': user_count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

# Add this to the bottom of your auth_server.py
if __name__ == '__main__':
    # Render sets the PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting server on port {port}")
    print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")
    
    try:
        init_db()
        print("Database initialized successfully")
        
        # Render requires host='0.0.0.0' and debug=False for production
        app.run(debug=False, host='0.0.0.0', port=port)
        
    except Exception as e:
        print(f"Failed to start server: {e}")