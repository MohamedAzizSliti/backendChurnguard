from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"

@dataclass
class EmailNotification:
    id: Optional[int] = None
    email: str = ""
    name: str = ""
    issue: str = ""
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmailNotification':
        return cls(
            id=data.get('id'),
            email=data.get('email', ''),
            name=data.get('name', ''),
            issue=data.get('issue', ''),
            status=NotificationStatus(data.get('status', 'pending')),
            created_at=datetime.fromisoformat(data.get('created_at').replace('Z', '+00:00')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data.get('updated_at').replace('Z', '+00:00')) if data.get('updated_at') else None,
            sent_at=datetime.fromisoformat(data.get('sent_at').replace('Z', '+00:00')) if data.get('sent_at') else None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'issue': self.issue,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        } 