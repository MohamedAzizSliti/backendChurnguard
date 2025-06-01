from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CustomerIssueDTO(BaseModel):
    customer_id: Optional[float] = None
    code_contrat: Optional[float] = None
    client_type: Optional[float] = None
    client_region: Optional[float] = None
    client_categorie: Optional[float] = None
    incident_title: Optional[str] = None
    churn_risk: Optional[float] = None
    status: str = "not sent"

class CustomerIssueCreateDTO(BaseModel):
    customer_id: Optional[float] = None
    code_contrat: Optional[float] = None
    client_type: Optional[float] = None
    client_region: Optional[float] = None
    client_categorie: Optional[float] = None
    incident_title: Optional[str] = None
    churn_risk: Optional[float] = None
    status: str = "not sent"

class CustomerIssueUpdateDTO(BaseModel):
    customer_id: Optional[float] = None
    code_contrat: Optional[float] = None
    client_type: Optional[float] = None
    client_region: Optional[float] = None
    client_categorie: Optional[float] = None
    incident_title: Optional[str] = None
    churn_risk: Optional[float] = None
    status: Optional[str] = None 