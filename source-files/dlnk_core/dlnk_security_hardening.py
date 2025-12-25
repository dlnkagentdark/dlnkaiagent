import os
import sqlite3
import logging
from functools import wraps
from flask import Flask, request, jsonify, session
from cryptography.fernet import Fernet
import bleach
import time

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Encryption at Rest ---
# Generate a key for encryption. In a real application, store this securely.
ENCRYPTION_KEY = Fernet.generate_key()
fernet = Fernet(ENCRYPTION_KEY)

# --- Database Setup ---
DATABASE = 'database.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    return db

@app.before_first_request
def create_tables():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
    """)
    db.commit()
    db.close()

# --- Security Functions ---

def sanitize_input(data):
    """Sanitizes user input to prevent XSS attacks."""
    return bleach.clean(data)

def generate_csrf_token():
    """Generate a CSRF token."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = os.urandom(24).hex()
    return session['_csrf_token']

def csrf_protected(f):
    """Decorator for CSRF protection."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            token = session.pop('_csrf_token', None)
            if not token or token != request.form.get('_csrf_token'):
                return jsonify({'error': 'Invalid CSRF token'}), 400
        return f(*args, **kwargs)
    return decorated_function

RATE_LIMIT = 5
RATE_LIMIT_PERIOD = 60  # in seconds
request_counts = {}

def rate_limit():
    """Decorator for rate limiting."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip_address = request.remote_addr
            current_time = time.time()

            if ip_address not in request_counts:
                request_counts[ip_address] = []

            # Remove requests older than the rate limit period
            request_counts[ip_address] = [t for t in request_counts[ip_address] if t > current_time - RATE_LIMIT_PERIOD]

            if len(request_counts[ip_address]) >= RATE_LIMIT:
                return jsonify({'error': 'Rate limit exceeded'}), 429

            request_counts[ip_address].append(current_time)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Routes ---

@app.route('/register', methods=['POST'])
@csrf_protected
@rate_limit()
def register():
    """Registers a new user."""
    data = request.get_json()
    username = sanitize_input(data.get('username'))
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Encrypt the password before storing
    encrypted_password = fernet.encrypt(password.encode()).decode('utf-8')

    try:
        db = get_db()
        cursor = db.cursor()
        # Use parameterized query to prevent SQL injection
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, encrypted_password))
        db.commit()
        logger.info(f'User {username} registered successfully.')
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    except Exception as e:
        logger.error(f'Error registering user: {e}')
        return jsonify({'error': 'An internal error occurred'}), 500
    finally:
        db.close()

@app.route('/login', methods=['POST'])
@csrf_protected
@rate_limit()
def login():
    """Logs in a user."""
    data = request.get_json()
    username = sanitize_input(data.get('username'))
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    try:
        db = get_db()
        cursor = db.cursor()
        # Use parameterized query to prevent SQL injection
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            decrypted_password = fernet.decrypt(user[0].encode()).decode('utf-8')
            if password == decrypted_password:
                session['user'] = username
                logger.info(f'User {username} logged in successfully.')
                return jsonify({'message': 'Login successful', 'csrf_token': generate_csrf_token()}), 200

        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        logger.error(f'Error logging in user: {e}')
        return jsonify({'error': 'An internal error occurred'}), 500
    finally:
        db.close()

@app.route('/profile')
def profile():
    """User profile page."""
    if 'user' in session:
        return jsonify({'message': f'Welcome {session["user"]}'})
    return jsonify({'error': 'Unauthorized'}), 401

@app.route('/get_csrf_token', methods=['GET'])
def get_csrf_token():
    """Endpoint to get a CSRF token."""
    return jsonify({'csrf_token': generate_csrf_token()})

if __name__ == '__main__':
    app.run(debug=True)
