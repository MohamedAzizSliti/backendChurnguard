from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta

@dataclass
class AuthToken:
    access_token: str
    token_type: str = "bearer"
    expires_at: Optional[datetime] = None
    
    @classmethod
    def create(cls, token: str, expires_in_minutes: int = 30) -> 'AuthToken':
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        return cls(
            access_token=token,
            token_type="bearer",
            expires_at=expires_at
        )
