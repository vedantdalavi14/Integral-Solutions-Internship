"""
Watch History Model

Tracks user video watch history including position for "continue watching" feature.
"""

from datetime import datetime
from bson import ObjectId
from app import get_db


class WatchHistory:
    """Model for tracking video watch history with position tracking"""
    
    collection_name = 'watch_history'
    
    def __init__(self, user_id, video_id, last_position=0, watch_duration=0, 
                 video_duration=0, completed=False, _id=None, created_at=None, updated_at=None):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.video_id = video_id
        self.last_position = last_position  # Current position in seconds (where user left off)
        self.watch_duration = watch_duration  # Total seconds watched
        self.video_duration = video_duration  # Total video length in seconds
        self.completed = completed  # Whether user finished the video
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary for database storage"""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'video_id': self.video_id,
            'last_position': self.last_position,
            'watch_duration': self.watch_duration,
            'video_duration': self.video_duration,
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
    def update_or_create(cls, user_id, video_id, last_position=0, watch_duration=0, 
                         video_duration=0, completed=False):
        """
        Update existing watch history or create new one.
        Uses upsert for atomic operation.
        
        Args:
            user_id: User's ID (string)
            video_id: Video's ID (string)
            last_position: Current playback position in seconds
            watch_duration: Total seconds watched in this session
            video_duration: Total video length in seconds
            completed: Whether video was completed
            
        Returns:
            Updated/created document
        """
        db = get_db()
        
        # Get existing record to accumulate watch_duration
        existing = db[cls.collection_name].find_one({
            'user_id': user_id, 
            'video_id': video_id
        })
        
        total_duration = watch_duration
        if existing:
            total_duration = existing.get('watch_duration', 0) + watch_duration
        
        update_data = {
            '$set': {
                'last_position': last_position,
                'watch_duration': total_duration,
                'video_duration': video_duration,
                'completed': completed or (existing and existing.get('completed', False)),
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
        
        # Return the updated document
        return db[cls.collection_name].find_one({
            'user_id': user_id, 
            'video_id': video_id
        })
    
    @classmethod
    def get_user_progress(cls, user_id, video_id):
        """
        Get user's watch progress for a specific video.
        
        Returns:
            dict with last_position, watch_duration, completed, progress_percent
        """
        db = get_db()
        record = db[cls.collection_name].find_one({
            'user_id': user_id,
            'video_id': video_id
        })
        
        if record:
            video_dur = record.get('video_duration', 0)
            last_pos = record.get('last_position', 0)
            progress_percent = (last_pos / video_dur * 100) if video_dur > 0 else 0
            
            return {
                'last_position': last_pos,
                'watch_duration': record.get('watch_duration', 0),
                'video_duration': video_dur,
                'completed': record.get('completed', False),
                'progress_percent': round(progress_percent, 1)
            }
        
        return {
            'last_position': 0,
            'watch_duration': 0,
            'video_duration': 0,
            'completed': False,
            'progress_percent': 0
        }
    
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
            last_position=data.get('last_position', 0),
            watch_duration=data.get('watch_duration', 0),
            video_duration=data.get('video_duration', 0),
            completed=data.get('completed', False),
            _id=data['_id'],
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
