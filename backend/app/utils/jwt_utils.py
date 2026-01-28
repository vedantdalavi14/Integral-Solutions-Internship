import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from app.config import Config

def generate_access_token(user_id):
    """Generate JWT access token for authentication"""
    payload = {
        'user_id': str(user_id),
        'exp': datetime.utcnow() + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES),
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

def decode_access_token(token):
    """Decode and verify JWT access token"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        if payload.get('type') != 'access':
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def generate_refresh_token(user_id):
    """
    Generate JWT refresh token for token rotation.
    Longer lived (7 days) than access tokens.
    """
    payload = {
        'user_id': str(user_id),
        'exp': datetime.utcnow() + timedelta(seconds=Config.REFRESH_TOKEN_EXPIRES),
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    return jwt.encode(payload, Config.REFRESH_TOKEN_SECRET, algorithm='HS256')


def decode_refresh_token(token):
    """Decode and verify JWT refresh token"""
    try:
        payload = jwt.decode(token, Config.REFRESH_TOKEN_SECRET, algorithms=['HS256'])
        if payload.get('type') != 'refresh':
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def jwt_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Authorization token is missing'}), 401
        
        payload = decode_access_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user_id to request context
        request.user_id = payload['user_id']
        return f(*args, **kwargs)
    
    return decorated


def generate_playback_token(video_id, user_id):
    """
    Generate short-lived playback token for video streaming
    This token is used to verify video access without exposing YouTube URLs
    """
    payload = {
        'video_id': str(video_id),
        'user_id': str(user_id),
        'exp': datetime.utcnow() + timedelta(seconds=Config.PLAYBACK_TOKEN_EXPIRES),
        'iat': datetime.utcnow(),
        'type': 'playback'
    }
    return jwt.encode(payload, Config.PLAYBACK_TOKEN_SECRET, algorithm='HS256')

def decode_playback_token(token):
    """Decode and verify playback token"""
    try:
        payload = jwt.decode(token, Config.PLAYBACK_TOKEN_SECRET, algorithms=['HS256'])
        if payload.get('type') != 'playback':
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def generate_internal_token(video_id, user_id):
    """
    Generate very short-lived internal token for the player page
    This is used for the 302 redirect to backend-owned player
    """
    payload = {
        'video_id': str(video_id),
        'user_id': str(user_id),
        'exp': datetime.utcnow() + timedelta(seconds=Config.INTERNAL_TOKEN_EXPIRES),
        'iat': datetime.utcnow(),
        'type': 'internal'
    }
    return jwt.encode(payload, Config.INTERNAL_TOKEN_SECRET, algorithm='HS256')

def decode_internal_token(token):
    """Decode and verify internal player token"""
    try:
        payload = jwt.decode(token, Config.INTERNAL_TOKEN_SECRET, algorithms=['HS256'])
        if payload.get('type') != 'internal':
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
