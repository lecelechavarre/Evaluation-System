"""
Data models and validation.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import re


class ValidationError(Exception):
    """Custom validation error."""
    pass


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_rating(rating: int, min_val: int = 1, max_val: int = 5) -> bool:
    """Validate rating is within range."""
    return min_val <= rating <= max_val


class User:
    """User model with validation."""
    
    @staticmethod
    def create(username: str, password: str, role: str,
              full_name: str, email: str) -> Dict:
        """Create validated user dictionary."""
        if not username or len(username) < 3:
            raise ValidationError("Username must be at least 3 characters")
        
        if not password or len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        
        if role not in ['admin', 'evaluator', 'employee']:
            raise ValidationError("Invalid role")
        
        if not validate_email(email):
            raise ValidationError("Invalid email format")
        
        return {
            'username': username,
            'password': password,  # Will be hashed by AuthManager
            'role': role,
            'full_name': full_name,
            'email': email
        }


class Criterion:
    """Evaluation criterion model."""
    
    @staticmethod
    def create(name: str, weight: float = 1.0, description: str = "") -> Dict:
        """Create validated criterion dictionary."""
        if not name or len(name) < 2:
            raise ValidationError("Criterion name must be at least 2 characters")
        
        if weight <= 0:
            raise ValidationError("Weight must be positive")
        
        return {
            'id': f"c-{uuid.uuid4().hex[:8]}",
            'name': name.strip(),
            'weight': float(weight),
            'description': description.strip(),
            'created_at': datetime.now().isoformat()
        }


class Evaluation:
    """Performance evaluation model."""
    
    @staticmethod
    def create(employee_id: str, evaluator_id: str, scores: Dict[str, int],
              comments: str = "", status: str = "draft") -> Dict:
        """Create validated evaluation dictionary."""
        if not employee_id or not evaluator_id:
            raise ValidationError("Employee and evaluator IDs required")
        
        if not scores:
            raise ValidationError("At least one score required")
        
        # Validate all scores
        for criterion_id, score in scores.items():
            if not validate_rating(score):
                raise ValidationError(f"Invalid score for {criterion_id}")
        
        if status not in ['draft', 'final', 'archived']:
            raise ValidationError("Invalid status")
        
        return {
            'id': f"ev-{uuid.uuid4().hex[:8]}",
            'employee_id': employee_id,
            'evaluator_id': evaluator_id,
            'date': datetime.now().date().isoformat(),
            'scores': scores,
            'comments': comments.strip(),
            'status': status,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }