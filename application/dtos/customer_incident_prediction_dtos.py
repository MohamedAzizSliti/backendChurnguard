from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from domain.entities.customer_incident_prediction import IncidentType

class CustomerIncidentPredictionDTO(BaseModel):
    id: Optional[int] = None
    customer_id: str
    client_region: str
    client_type: str
    client_category: Optional[float] = None
    q1_prediction: float = 0.0
    q2_prediction: float = 0.0
    q3_prediction: float = 0.0
    q4_prediction: float = 0.0
    most_likely_incident: IncidentType
    recommendation: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    avg_risk_percentage: Optional[float] = None
    risk_level: Optional[str] = None

class CustomerIncidentPredictionCreateDTO(BaseModel):
    customer_id: str
    client_region: str
    client_type: str
    client_category: Optional[float] = None
    q1_prediction: float = 0.0
    q2_prediction: float = 0.0
    q3_prediction: float = 0.0
    q4_prediction: float = 0.0
    most_likely_incident: IncidentType
    recommendation: str

class CustomerIncidentPredictionUpdateDTO(BaseModel):
    customer_id: Optional[str] = None
    client_region: Optional[str] = None
    client_type: Optional[str] = None
    client_category: Optional[float] = None
    q1_prediction: Optional[float] = None
    q2_prediction: Optional[float] = None
    q3_prediction: Optional[float] = None
    q4_prediction: Optional[float] = None
    most_likely_incident: Optional[IncidentType] = None
    recommendation: Optional[str] = None

class CustomerRiskAnalysisDTO(BaseModel):
    """DTO for the customer_risk_analysis view"""
    id: int
    customer_id: str
    client_region: str
    client_type: str
    client_category: Optional[float] = None
    q1_prediction: float
    q2_prediction: float
    q3_prediction: float
    q4_prediction: float
    most_likely_incident: IncidentType
    recommendation: str
    created_at: datetime
    updated_at: datetime
    avg_risk_percentage: float
    risk_level: str 