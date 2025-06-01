from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class CustomerIssue:
    customer_id: Optional[float] = None
    code_contrat: Optional[float] = None
    client_type: Optional[float] = None
    client_region: Optional[float] = None
    client_categorie: Optional[float] = None
    incident_title: Optional[str] = None
    churn_risk: Optional[float] = None
    status: str = "not sent"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomerIssue':
        return cls(
            customer_id=float(data.get('customer_id')) if data.get('customer_id') is not None else None,
            code_contrat=float(data.get('code_contrat')) if data.get('code_contrat') is not None else None,
            client_type=float(data.get('client_type')) if data.get('client_type') is not None else None,
            client_region=float(data.get('client_region')) if data.get('client_region') is not None else None,
            client_categorie=float(data.get('client_categorie')) if data.get('client_categorie') is not None else None,
            incident_title=data.get('incident_title'),
            churn_risk=float(data.get('churn_risk')) if data.get('churn_risk') is not None else None,
            status=data.get('status', 'not sent')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'customer_id': self.customer_id,
            'code_contrat': self.code_contrat,
            'client_type': self.client_type,
            'client_region': self.client_region,
            'client_categorie': self.client_categorie,
            'incident_title': self.incident_title,
            'churn_risk': self.churn_risk,
            'status': self.status
        } 