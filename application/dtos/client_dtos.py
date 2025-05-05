from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ContactDTO(BaseModel):
    primary: str
    secondary: Optional[str] = None
    preferred_time: Optional[str] = None
    last_call: Optional[str] = None

class ClientDTO(BaseModel):
    id: str
    name: str
    segment: str
    since: str
    churn_risk: int
    contacts: Optional[ContactDTO] = None
    
class ClientDetailDTO(ClientDTO):
    monthly_revenue: Optional[str] = None
    churn_trend: Optional[str] = None
    churn_trend_days: Optional[int] = None
    factors: List[Dict[str, Any]] = []
    interactions: List[Dict[str, Any]] = []
    recommendations: List[Dict[str, Any]] = []

class ClientCreateDTO(BaseModel):
    name: str
    segment: str
    since: str
    churn_risk: int
    contacts: ContactDTO
    monthly_revenue: Optional[str] = None
    churn_trend: Optional[str] = None
    churn_trend_days: Optional[int] = None
