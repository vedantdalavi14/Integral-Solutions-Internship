import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Atlas Connection
    MONGO_URI = os.getenv(
        'MONGO_URI',
        'mongodb+srv://vedantdalavi14_db_user:TsBMzbIgioY0gVQo@cluster0.obxxlpy.mongodb.net/video_app?retryWrites=true&w=majority'
    )
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super-secret-jwt-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24 hours in seconds
    
    # Playback Token Configuration (short-lived for video streaming)
    PLAYBACK_TOKEN_SECRET = os.getenv('PLAYBACK_TOKEN_SECRET', 'playback-secret-key-change-in-production')
    PLAYBACK_TOKEN_EXPIRES = 5 * 60  # 5 minutes in seconds
    
    # Internal Player Token (very short-lived)
    INTERNAL_TOKEN_SECRET = os.getenv('INTERNAL_TOKEN_SECRET', 'internal-token-secret-key')
    INTERNAL_TOKEN_EXPIRES = 60  # 1 minute in seconds
