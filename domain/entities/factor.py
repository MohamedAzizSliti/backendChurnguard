from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class Factor:
    id: str
    client_id: str
    name: str
    percentage: int
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Factor':
        return cls(
            id=data.get('id', ''),
            client_id=data.get('clientId', ''),
            name=data.get('name', ''),
            percentage=data.get('percentage', 0),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else datetime.now()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'clientId': self.client_id,
            'name': self.name,
            'percentage': self.percentage,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
