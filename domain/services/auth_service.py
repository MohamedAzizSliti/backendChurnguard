from domain.entities.user import User
from domain.value_objects.auth_token import AuthToken
from typing import Optional

class AuthService:
    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password strength"""
        # Implement password validation logic
        return len(password) >= 8
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        # Implement email validation logic
        return "@" in email
