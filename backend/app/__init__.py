"""
Flask Application Factory

This module creates and configures the Flask application.
Includes MongoDB connection, CORS setup, rate limiting, and blueprint registration.
"""

import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient
from app.config import Config

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

def setup_logging():
    """Configure application-wide logging"""
    # Create logger
    logger = logging.getLogger('video_app')
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # File handler (logs everything)
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Initialize logger
logger = setup_logging()

# =============================================================================
# RATE LIMITER
# =============================================================================

# Initialize rate limiter (will be attached to app in create_app)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

def get_limiter():
    """Get the rate limiter instance"""
    return limiter

# =============================================================================
# DATABASE
# =============================================================================

mongo_client = None
db = None

def get_db():
    """Get the database instance"""
    global db
    return db

def get_logger():
    """Get the application logger"""
    return logger

# =============================================================================
# APPLICATION FACTORY
# =============================================================================

def create_app():
    """
    Application factory function.
    Creates and configures the Flask application.
    """
    global mongo_client, db
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for React Native app
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Initialize rate limiter
    limiter.init_app(app)
    logger.info("Rate limiter initialized")
    
    # Custom error handler for rate limit exceeded
    @app.errorhandler(429)
    def ratelimit_handler(e):
        logger.warning(f"Rate limit exceeded: {get_remote_address()}")
        return jsonify({
            'error': 'Too many requests. Please try again later.',
            'retry_after': e.description
        }), 429
    
    # Initialize MongoDB connection with SSL certificates
    try:
        import certifi
        # First try with proper SSL certificates
        try:
            mongo_client = MongoClient(
                Config.MONGO_URI,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=5000
            )
            db = mongo_client.video_app
            mongo_client.admin.command('ping')
        except Exception as ssl_error:
            # Fallback: try with relaxed SSL (development only)
            logger.warning(f"SSL connection failed, trying fallback: {ssl_error}")
            mongo_client = MongoClient(
                Config.MONGO_URI,
                tls=True,
                tlsAllowInvalidCertificates=True,
                serverSelectionTimeoutMS=10000
            )
            db = mongo_client.video_app
            mongo_client.admin.command('ping')
        
        logger.info("Connected to MongoDB Atlas successfully")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise e
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.video import video_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(video_bp)
    
    logger.info("Flask application initialized")
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'database': 'connected'}
    
    return app
