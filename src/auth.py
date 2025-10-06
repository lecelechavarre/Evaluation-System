"""
Authentication and user management.
"""
import bcrypt
import uuid
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def hash_password(plain_password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


class AuthManager:
    """Manages user authentication and sessions."""
    
    def __init__(self, user_store):
        self.user_store = user_store
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with username and password."""
        users = self.user_store.find_by(username=username)
        if not users:
            logger.warning(f"Authentication failed: user {username} not found")
            return None
        
        user = users[0]
        if verify_password(password, user['password_hash']):
            logger.info(f"User {username} authenticated successfully")
            # Return user without password hash
            safe_user = {k: v for k, v in user.items() if k != 'password_hash'}
            return safe_user
        
        logger.warning(f"Authentication failed: invalid password for {username}")
        return None
    
    def create_user(self, username: str, password: str, role: str,
                   full_name: str, email: str) -> Optional[str]:
        """Create a new user."""
        # Check if username already exists
        if self.user_store.find_by(username=username):
            logger.warning(f"User creation failed: {username} already exists")
            return None
        
        user_id = f"u-{uuid.uuid4().hex[:8]}"
        user = {
            'id': user_id,
            'username': username,
            'password_hash': hash_password(password),
            'role': role,
            'full_name': full_name,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'active': True
        }
        
        if self.user_store.create(user):
            logger.info(f"Created user: {username} ({role})")
            return user_id
        return None
    
    def change_password(self, user_id: str, old_password: str,
                       new_password: str) -> bool:
        """Change user password."""
        user = self.user_store.find_by_id(user_id)
        if not user:
            return False
        
        if not verify_password(old_password, user['password_hash']):
            logger.warning(f"Password change failed: incorrect old password")
            return False
        
        new_hash = hash_password(new_password)
        return self.user_store.update(user_id, {'password_hash': new_hash})
    
    def reset_password(self, user_id: str, new_password: str) -> bool:
        """Admin reset user password."""
        new_hash = hash_password(new_password)
        return self.user_store.update(user_id, {'password_hash': new_hash})
