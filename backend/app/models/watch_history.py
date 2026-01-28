"""
Watch History Model

Tracks user video watch history for analytics and recommendations.
"""

from datetime import datetime
from bson import ObjectId
from app import get_db


class WatchHistory:
    """Model for tracking video watch history"""
    
    collection_name = 'watch_history'
    
    def __init__(self, user_id, video_id, watch_duration=0, completed=False, 
                 _id=None, created_at=None, updated_at=None):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.video_id = video_id
        self.watch_duration = watch_duration  # seconds watched
        self.completed = completed  # whether user finished the video
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary for database storage"""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'video_id': self.video_id,
            'watch_duration': self.watch_duration,
            'completed': self.completed,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def save(self):
        """Save watch history to database"""
        db = get_db()
        self.updated_at = datetime.utcnow()
        result = db[self.collection_name].insert_one(self.to_dict())
        return result.inserted_id
    
    @classmethod
    def update_or_create(cls, user_id, video_id, watch_duration, completed=False):
        """
        Update existing watch history or create new one.
        Uses upsert for atomic operation.
        
        Args:
            user_id: User's ID (string)
            video_id: Video's ID (string)
            watch_duration: Seconds watched
            completed: Whether video was completed
            
        Returns:
            WatchHistory instance
        """
        db = get_db()
        
        update_data = {
            '$set': {
                'watch_duration': watch_duration,
                'completed': completed,
                'updated_at': datetime.utcnow()
            },
            '$setOnInsert': {
                'user_id': user_id,
                'video_id': video_id,
                'created_at': datetime.utcnow()
            }
        }
        
        result = db[cls.collection_name].update_one(
            {'user_id': user_id, 'video_id': video_id},
            update_data,
            upsert=True
        )
        
        return result
    
    @classmethod
    def get_user_history(cls, user_id, limit=20):
        """
        Get watch history for a user.
        
        Args:
            user_id: User's ID
            limit: Maximum number of records to return
            
        Returns:
            List of watch history records
        """
        db = get_db()
        cursor = db[cls.collection_name].find(
            {'user_id': user_id}
        ).sort('updated_at', -1).limit(limit)
        
        return [cls._from_dict(doc) for doc in cursor]
    
    @classmethod
    def get_video_stats(cls, video_id):
        """
        Get watch statistics for a video.
        
        Returns:
            dict with view_count, total_watch_time, completion_count
        """
        db = get_db()
        
        pipeline = [
            {'$match': {'video_id': video_id}},
            {'$group': {
                '_id': '$video_id',
                'view_count': {'$sum': 1},
                'total_watch_time': {'$sum': '$watch_duration'},
                'completion_count': {'$sum': {'$cond': ['$completed', 1, 0]}}
            }}
        ]
        
        result = list(db[cls.collection_name].aggregate(pipeline))
        
        if result:
            return {
                'view_count': result[0]['view_count'],
                'total_watch_time': result[0]['total_watch_time'],
                'completion_count': result[0]['completion_count']
            }
        
        return {
            'view_count': 0,
            'total_watch_time': 0,
            'completion_count': 0
        }
    
    @classmethod
    def _from_dict(cls, data):
        """Create WatchHistory instance from dictionary"""
        return cls(
            user_id=data['user_id'],
            video_id=data['video_id'],
            watch_duration=data.get('watch_duration', 0),
            completed=data.get('completed', False),
            _id=data['_id'],
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
