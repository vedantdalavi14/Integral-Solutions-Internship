from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from app.config import Config

# MongoDB client instance
mongo_client = None
db = None

def get_db():
    """Get the database instance"""
    global db
    return db

def create_app():
    """Application factory"""
    global mongo_client, db
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for React Native app
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Initialize MongoDB connection
    try:
        mongo_client = MongoClient(Config.MONGO_URI)
        db = mongo_client.video_app
        # Test connection
        mongo_client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas successfully!")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise e
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.video import video_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(video_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'database': 'connected'}
    
    return app
