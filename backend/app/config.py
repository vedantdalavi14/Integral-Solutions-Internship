import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Atlas Connection (REQUIRED - set in environment variables)
    MONGO_URI = os.getenv('MONGO_URI')
    if not MONGO_URI:
        # For local development, you can create a .env file with MONGO_URI
        raise ValueError("MONGO_URI environment variable is required!")
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super-secret-jwt-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 15 * 60  # 15 minutes (shorter for security with refresh tokens)
    
    # Refresh Token Configuration (long-lived)
    REFRESH_TOKEN_SECRET = os.getenv('REFRESH_TOKEN_SECRET', 'refresh-secret-key-change-in-production')
    REFRESH_TOKEN_EXPIRES = 7 * 24 * 60 * 60  # 7 days in seconds
    
    # Playback Token Configuration (short-lived for video streaming)
    PLAYBACK_TOKEN_SECRET = os.getenv('PLAYBACK_TOKEN_SECRET', 'playback-secret-key-change-in-production')
    PLAYBACK_TOKEN_EXPIRES = 5 * 60  # 5 minutes in seconds
    
    # Internal Player Token (very short-lived)
    INTERNAL_TOKEN_SECRET = os.getenv('INTERNAL_TOKEN_SECRET', 'internal-token-secret-key')
    INTERNAL_TOKEN_EXPIRES = 60  # 1 minute in seconds

