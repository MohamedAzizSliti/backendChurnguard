from pydantic import BaseModel
from typing import List, Dict, Any

class ChurnTrendsDTO(BaseModel):
    months: List[str]
    churn_rates: List[float]

class ChurnSegmentDTO(BaseModel):
    name: str
    percentage: int
    color: str

class ChurnBySegmentDTO(BaseModel):
    segments: List[ChurnSegmentDTO]

class ChurnFactorDTO(BaseModel):
    name: str
    percentage: int

class ChurnFactorsDTO(BaseModel):
    factors: List[ChurnFactorDTO]

class RetentionActionDTO(BaseModel):
    name: str
    effectiveness: int
    cost: int
    roi: int

class RetentionActionsDTO(BaseModel):
    actions: List[RetentionActionDTO]
