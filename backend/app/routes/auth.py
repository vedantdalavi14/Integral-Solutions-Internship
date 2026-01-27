from flask import Blueprint, request, jsonify
from app.models.user import User
from app.utils.jwt_utils import generate_access_token, jwt_required
from app import get_db

auth_bp = Blueprint('auth', __name__)

# Token blacklist (in production, use Redis)
token_blacklist = set()


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Register a new user
    
    Request Body:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "securepassword123"
    }
    """
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    if not password or len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Check if user already exists
    existing_user = User.find_by_email(email)
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create new user
    password_hash = User.hash_password(password)
    user = User(name=name, email=email, password_hash=password_hash)
    user.save()
    
    # Generate access token
    access_token = generate_access_token(user._id)
    
    return jsonify({
        'message': 'User registered successfully',
        'access_token': access_token,
        'user': user.to_public_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT
    
    Request Body:
    {
        "email": "john@example.com",
        "password": "securepassword123"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    if not password:
        return jsonify({'error': 'Password is required'}), 400
    
    # Find user by email
    user = User.find_by_email(email)
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Verify password
    if not User.verify_password(password, user.password_hash):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Generate access token
    access_token = generate_access_token(user._id)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_public_dict()
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required
def get_profile():
    """
    Get current user profile (protected route)
    
    Headers:
    Authorization: Bearer <access_token>
    """
    user = User.find_by_id(request.user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': user.to_public_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    """
    Logout user (invalidate token)
    
    Headers:
    Authorization: Bearer <access_token>
    
    Note: In production, implement proper token blacklisting with Redis
    """
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        token_blacklist.add(token)
    
    return jsonify({
        'message': 'Logged out successfully'
    }), 200
