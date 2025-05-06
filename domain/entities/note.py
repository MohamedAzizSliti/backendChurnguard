from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime

@dataclass
class Note:
    id: str
    title: str
    description: str
    sender_id: str
    recipients: List[str]  # Array of role strings
    is_read: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Note':
        return cls(
            id=data.get('id', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            sender_id=data.get('sender_id', ''),
            recipients=data.get('recipients', []),
            is_read=data.get('is_read', False),
            timestamp=datetime.fromisoformat(data.get('timestamp')) if data.get('timestamp') else datetime.now()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'sender_id': self.sender_id,
            'recipients': self.recipients,
            'is_read': self.is_read,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        } 