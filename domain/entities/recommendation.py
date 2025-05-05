from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class Recommendation:
    id: str
    client_id: str
    title: str
    impact: int
    details: str
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Recommendation':
        return cls(
            id=data.get('id', ''),
            client_id=data.get('clientId', ''),
            title=data.get('title', ''),
            impact=data.get('impact', 0),
            details=data.get('details', ''),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else datetime.now()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'clientId': self.client_id,
            'title': self.title,
            'impact': self.impact,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
