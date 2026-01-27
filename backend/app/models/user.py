from datetime import datetime
from bson import ObjectId
import bcrypt
from app import get_db

class User:
    """User model for authentication"""
    
    collection_name = 'users'
    
    def __init__(self, name, email, password_hash, _id=None, created_at=None):
        self._id = _id or ObjectId()
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            '_id': self._id,
            'name': self.name,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at
        }
    
    def to_public_dict(self):
        """Convert user to public dictionary (no password)"""
        return {
            'id': str(self._id),
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }
    
    def save(self):
        """Save user to database"""
        db = get_db()
        result = db[self.collection_name].insert_one(self.to_dict())
        return result.inserted_id
    
    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)
    
    @staticmethod
    def verify_password(password, password_hash):
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash)
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        db = get_db()
        user_data = db[cls.collection_name].find_one({'email': email})
        if user_data:
            return cls(
                name=user_data['name'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                _id=user_data['_id'],
                created_at=user_data.get('created_at')
            )
        return None
    
    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID"""
        db = get_db()
        try:
            user_data = db[cls.collection_name].find_one({'_id': ObjectId(user_id)})
            if user_data:
                return cls(
                    name=user_data['name'],
                    email=user_data['email'],
                    password_hash=user_data['password_hash'],
                    _id=user_data['_id'],
                    created_at=user_data.get('created_at')
                )
        except:
            pass
        return None
