# Routes package
from app.routes.auth import auth_bp
from app.routes.video import video_bp

__all__ = ['auth_bp', 'video_bp']
