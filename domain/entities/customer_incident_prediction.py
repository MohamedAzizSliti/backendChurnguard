from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from decimal import Decimal

class IncidentType(str, Enum):
    INTERNET_PROBLEM = "internet_problem"
    WIFI_ISSUE = "wifi_issue"
    HARDWARE_CONFIG = "hardware_config"
    SLOW_CONNECTION = "slow_connection"
    DISCONNECTION = "disconnection"
    OTHER_INCIDENT = "other_incident"

@dataclass
class CustomerIncidentPrediction:
    id: Optional[int] = None
    customer_id: str = ""
    client_region: str = ""
    client_type: str = ""
    client_category: Optional[Decimal] = None
    q1_prediction: Decimal = Decimal('0.0')
    q2_prediction: Decimal = Decimal('0.0')
    q3_prediction: Decimal = Decimal('0.0')
    q4_prediction: Decimal = Decimal('0.0')
    most_likely_incident: IncidentType = IncidentType.OTHER_INCIDENT
    recommendation: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomerIncidentPrediction':
        return cls(
            id=data.get('id'),
            customer_id=data.get('customer_id', ''),
            client_region=data.get('client_region', ''),
            client_type=data.get('client_type', ''),
            client_category=Decimal(str(data.get('client_category'))) if data.get('client_category') is not None else None,
            q1_prediction=Decimal(str(data.get('q1_prediction', '0.0'))),
            q2_prediction=Decimal(str(data.get('q2_prediction', '0.0'))),
            q3_prediction=Decimal(str(data.get('q3_prediction', '0.0'))),
            q4_prediction=Decimal(str(data.get('q4_prediction', '0.0'))),
            most_likely_incident=IncidentType(data.get('most_likely_incident', 'other_incident')),
            recommendation=data.get('recommendation', ''),
            created_at=datetime.fromisoformat(data.get('created_at').replace('Z', '+00:00')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data.get('updated_at').replace('Z', '+00:00')) if data.get('updated_at') else None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'client_region': self.client_region,
            'client_type': self.client_type,
            'client_category': float(self.client_category) if self.client_category is not None else None,
            'q1_prediction': float(self.q1_prediction),
            'q2_prediction': float(self.q2_prediction),
            'q3_prediction': float(self.q3_prediction),
            'q4_prediction': float(self.q4_prediction),
            'most_likely_incident': self.most_likely_incident.value,
            'recommendation': self.recommendation,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_average_risk_percentage(self) -> float:
        """Calculate average risk percentage across all quarters"""
        return float((self.q1_prediction + self.q2_prediction + self.q3_prediction + self.q4_prediction) / 4)
    
    def get_risk_level(self) -> str:
        """Get risk level based on average risk percentage"""
        avg_risk = self.get_average_risk_percentage()
        if avg_risk >= 60:
            return "High"
        elif avg_risk >= 30:
            return "Medium"
        else:
            return "Low" 