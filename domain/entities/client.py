from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

@dataclass
class Contact:
    primary: str
    secondary: Optional[str] = None
    preferred_time: Optional[str] = None
    last_call: Optional[str] = None

@dataclass
class Client:
    id: str
    name: str
    segment: str
    since: str
    churn_risk: str
    contacts: Contact
    monthly_revenue: Optional[str] = None
    churn_trend: Optional[str] = None
    churn_trend_days: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Client':
        contacts_data = data.get('contacts', {})
        contacts = Contact(
            primary=contacts_data.get('primary', ''),
            secondary=contacts_data.get('secondary'),
            preferred_time=contacts_data.get('preferred_time'),
            last_call=contacts_data.get('last_call')
        )
        
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            segment=data.get('segment', ''),
            since=data.get('since', ''),
            churn_risk=data.get('churn_risk', ''),  # Use snake_case
            contacts=contacts,
            monthly_revenue=float(data.get('monthly_revenue')) if data.get('monthly_revenue') is not None else None,
            churn_trend=data.get('churn_trend'),
            churn_trend_days=data.get('churn_trend_days'),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data.get('updated_at')) if data.get('updated_at') else None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'segment': self.segment,
            'since': self.since,
            'churn_risk': self.churn_risk,  # Use snake_case
            'contacts': {
                'primary': self.contacts.primary,
                'secondary': self.contacts.secondary,
                'preferred_time': self.contacts.preferred_time,
                'last_call': self.contacts.last_call
            },
            'monthly_revenue': self.monthly_revenue,
            'churn_trend': self.churn_trend,
            'churn_trend_days': self.churn_trend_days,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
