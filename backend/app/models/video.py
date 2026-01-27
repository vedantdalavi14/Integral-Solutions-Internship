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
                    'title': 'How Startups Fail',
                    'description': 'Lessons from real founders about common startup pitfalls and how to avoid them.',
                    'youtube_id': 'dQw4w9WgXcQ',
                    'thumbnail_url': 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
                    'is_active': True,
                    'created_at': datetime.utcnow()
                },
                {
                    'title': 'Building Products Users Love',
                    'description': 'Key principles for creating successful products that users cant live without.',
                    'youtube_id': 'kYfNvmF0Bqw',
                    'thumbnail_url': 'https://img.youtube.com/vi/kYfNvmF0Bqw/maxresdefault.jpg',
                    'is_active': True,
                    'created_at': datetime.utcnow()
                }
            ]
            db[cls.collection_name].insert_many(videos)
            print("✅ Video data seeded successfully!")
            return True
        return False
