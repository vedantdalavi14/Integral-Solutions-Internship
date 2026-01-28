from datetime import datetime
from bson import ObjectId
from app import get_db

class Video:
    """Video model - YouTube abstraction layer"""
    
    collection_name = 'videos'
    
    def __init__(self, title, description, youtube_id, thumbnail_url, is_active=True, _id=None, created_at=None):
        self._id = _id or ObjectId()
        self.title = title
        self.description = description
        self.youtube_id = youtube_id  # NEVER exposed to frontend
        self.thumbnail_url = thumbnail_url
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert video to dictionary (internal use)"""
        return {
            '_id': self._id,
            'title': self.title,
            'description': self.description,
            'youtube_id': self.youtube_id,
            'thumbnail_url': self.thumbnail_url,
            'is_active': self.is_active,
            'created_at': self.created_at
        }
    
    def to_public_dict(self, playback_token=None):
        """
        Convert video to public dictionary (for API response)
        IMPORTANT: youtube_id is NEVER included here
        """
        data = {
            'id': str(self._id),
            'title': self.title,
            'description': self.description,
            'thumbnail_url': self.thumbnail_url
        }
        if playback_token:
            data['playback_token'] = playback_token
        return data
    
    def save(self):
        """Save video to database"""
        db = get_db()
        result = db[self.collection_name].insert_one(self.to_dict())
        return result.inserted_id
    
    @classmethod
    def find_active(cls, limit=2):
        """Find active videos (limited)"""
        db = get_db()
        videos = db[cls.collection_name].find({'is_active': True}).limit(limit)
        return [cls._from_dict(v) for v in videos]
    
    @classmethod
    def find_active_paginated(cls, page=1, limit=10):
        """
        Find active videos with pagination support.
        
        Args:
            page: Page number (1-indexed)
            limit: Number of items per page
            
        Returns:
            tuple: (videos list, total count)
        """
        db = get_db()
        skip = (page - 1) * limit
        
        # Get total count for pagination metadata
        total = db[cls.collection_name].count_documents({'is_active': True})
        
        # Get paginated videos
        cursor = db[cls.collection_name].find({'is_active': True}).skip(skip).limit(limit)
        videos = [cls._from_dict(v) for v in cursor]
        
        return videos, total
    
    @classmethod
    def find_by_id(cls, video_id):
        """Find video by ID"""
        db = get_db()
        try:
            video_data = db[cls.collection_name].find_one({'_id': ObjectId(video_id)})
            if video_data:
                return cls._from_dict(video_data)
        except:
            pass
        return None
    
    @classmethod
    def _from_dict(cls, data):
        """Create Video instance from dictionary"""
        return cls(
            title=data['title'],
            description=data['description'],
            youtube_id=data['youtube_id'],
            thumbnail_url=data['thumbnail_url'],
            is_active=data.get('is_active', True),
            _id=data['_id'],
            created_at=data.get('created_at')
        )
    
    @classmethod
    def seed_data(cls):
        """Seed initial video data if collection is empty"""
        db = get_db()
        if db[cls.collection_name].count_documents({}) == 0:
            videos = [
                {
                    'title': 'How to Start a Startup',
                    'description': 'Sam Altman and Dustin Moskovitz share key insights on starting a successful startup.',
                    'youtube_id': 'CBYhVcO4WgI',
                    'thumbnail_url': 'https://img.youtube.com/vi/CBYhVcO4WgI/maxresdefault.jpg',
                    'is_active': True,
                    'created_at': datetime.utcnow()
                },
                {
                    'title': 'React Native Tutorial for Beginners',
                    'description': 'Learn React Native from scratch and build mobile apps.',
                    'youtube_id': '0-S5a0eXPoc',
                    'thumbnail_url': 'https://img.youtube.com/vi/0-S5a0eXPoc/maxresdefault.jpg',
                    'is_active': True,
                    'created_at': datetime.utcnow()
                },
                {
                    'title': 'Python Tutorial - Full Course',
                    'description': 'Complete Python programming tutorial for beginners.',
                    'youtube_id': '_uQrJ0TkZlc',
                    'thumbnail_url': 'https://img.youtube.com/vi/_uQrJ0TkZlc/maxresdefault.jpg',
                    'is_active': True,
                    'created_at': datetime.utcnow()
                },
                {
                    'title': 'MongoDB Tutorial for Beginners',
                    'description': 'Learn MongoDB from basics to advanced concepts.',
                    'youtube_id': 'ofme2o29ngU',
                    'thumbnail_url': 'https://img.youtube.com/vi/ofme2o29ngU/maxresdefault.jpg',
                    'is_active': True,
                    'created_at': datetime.utcnow()
                },
                {
                    'title': 'Flask Web Development Tutorial',
                    'description': 'Build web applications with Python Flask framework.',
                    'youtube_id': 'Z1RJmh_OqeA',
                    'thumbnail_url': 'https://img.youtube.com/vi/Z1RJmh_OqeA/maxresdefault.jpg',
                    'is_active': True,
                    'created_at': datetime.utcnow()
                },
                {
                    'title': 'JavaScript Full Course',
                    'description': 'Master JavaScript from beginner to advanced level.',
                    'youtube_id': 'PkZNo7MFNFg',
                    'thumbnail_url': 'https://img.youtube.com/vi/PkZNo7MFNFg/maxresdefault.jpg',
                    'is_active': True,
                    'created_at': datetime.utcnow()
                },
                {
                    'title': 'Docker Tutorial for Beginners',
                    'description': 'Learn Docker containerization from scratch.',
                    'youtube_id': 'fqMOX6JJhGo',
                    'thumbnail_url': 'https://img.youtube.com/vi/fqMOX6JJhGo/maxresdefault.jpg',
                    'is_active': True,
                    'created_at': datetime.utcnow()
                },
                {
                    'title': 'Git and GitHub for Beginners',
                    'description': 'Complete guide to version control with Git.',
                    'youtube_id': 'RGOj5yH7evk',
                    'thumbnail_url': 'https://img.youtube.com/vi/RGOj5yH7evk/maxresdefault.jpg',
                    'is_active': True,
                    'created_at': datetime.utcnow()
                },
                {
                    'title': 'Machine Learning Full Course',
                    'description': 'Introduction to Machine Learning concepts and algorithms.',
                    'youtube_id': 'Gv9_4yMHFhI',
                    'thumbnail_url': 'https://img.youtube.com/vi/Gv9_4yMHFhI/maxresdefault.jpg',
                    'is_active': True,
                    'created_at': datetime.utcnow()
                },
                {
                    'title': 'REST API Design Best Practices',
                    'description': 'Learn how to design and build professional REST APIs.',
                    'youtube_id': '-MTSQjw5DrM',
                    'thumbnail_url': 'https://img.youtube.com/vi/-MTSQjw5DrM/maxresdefault.jpg',
                    'is_active': True,
                    'created_at': datetime.utcnow()
                }
            ]
            db[cls.collection_name].insert_many(videos)
            print("✅ Video data seeded successfully!")
            return True
        return False
