"""
Authentication Routes

Handles user signup, login, logout, token refresh, and profile endpoints.
Uses JWT for authentication with rate limiting on sensitive endpoints.
Implements refresh token flow for secure token rotation.
"""

from flask import Blueprint, request, jsonify
from app.models.user import User
from app.utils.jwt_utils import (
    generate_access_token,
    generate_refresh_token,
    decode_refresh_token,
    jwt_required
)
from app import get_db, get_logger, get_limiter

auth_bp = Blueprint('auth', __name__)
logger = get_logger()
limiter = get_limiter()

# Token blacklist (in production, use Redis)
token_blacklist = set()


@auth_bp.route('/signup', methods=['POST'])
@limiter.limit("3 per minute")  # Rate limit: 3 signups per minute per IP
def signup():
    """
    Register a new user.
    
    Returns both access_token (15 min) and refresh_token (7 days).
    
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
        logger.warning(f"Signup attempt with existing email: {email}")
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create new user
    password_hash = User.hash_password(password)
    user = User(name=name, email=email, password_hash=password_hash)
    user.save()
    
    logger.info(f"New user registered: {email}")
    
    # Generate both tokens
    access_token = generate_access_token(user._id)
    refresh_token = generate_refresh_token(user._id)
    
    return jsonify({
        'message': 'User registered successfully',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_public_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("3 per minute")  # Rate limit: 3 login attempts per minute per IP
def login():
    """
    Authenticate user and return JWT tokens.
    
    Returns both access_token (15 min) and refresh_token (7 days).
    
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
        logger.warning(f"Login failed - user not found: {email}")
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Verify password
    if not User.verify_password(password, user.password_hash):
        logger.warning(f"Login failed - invalid password: {email}")
        return jsonify({'error': 'Invalid email or password'}), 401
    
    logger.info(f"User logged in: {email}")
    
    # Generate both tokens
    access_token = generate_access_token(user._id)
    refresh_token = generate_refresh_token(user._id)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_public_dict()
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limit for refresh
def refresh_tokens():
    """
    Refresh access token using refresh token.
    
    Request Body:
    {
        "refresh_token": "eyJ..."
    }
    
    Response:
    {
        "access_token": "eyJ...",
        "refresh_token": "eyJ..."  // New refresh token (rotation)
    }
    """
    data = request.get_json()
    
    if not data or not data.get('refresh_token'):
        return jsonify({'error': 'Refresh token is required'}), 400
    
    refresh_token = data.get('refresh_token')
    
    # Decode and verify refresh token
    payload = decode_refresh_token(refresh_token)
    if not payload:
        logger.warning("Invalid or expired refresh token")
        return jsonify({'error': 'Invalid or expired refresh token'}), 401
    
    user_id = payload.get('user_id')
    
    # Verify user still exists
    user = User.find_by_id(user_id)
    if not user:
        logger.warning(f"Refresh failed - user not found: {user_id}")
        return jsonify({'error': 'User not found'}), 401
    
    logger.info(f"Token refreshed for user: {user.email}")
    
    # Generate new tokens (token rotation for security)
    new_access_token = generate_access_token(user._id)
    new_refresh_token = generate_refresh_token(user._id)
    
    return jsonify({
        'access_token': new_access_token,
        'refresh_token': new_refresh_token
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required
def get_profile():
    """
    Get current user profile (protected route).
    
    Headers:
    Authorization: Bearer <access_token>
    """
    user = User.find_by_id(request.user_id)
    if not user:
        logger.warning(f"Profile request - user not found: {request.user_id}")
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': user.to_public_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    """
    Logout user (invalidate token).
    
    Headers:
    Authorization: Bearer <access_token>
    
    Note: In production, implement proper token blacklisting with Redis
    """
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        token_blacklist.add(token)
    
    logger.info(f"User logged out: {request.user_id}")
    
    return jsonify({
        'message': 'Logged out successfully'
    }), 200
