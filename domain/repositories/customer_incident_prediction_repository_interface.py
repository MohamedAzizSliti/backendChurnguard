from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from domain.entities.customer_incident_prediction import CustomerIncidentPrediction, IncidentType

class CustomerIncidentPredictionRepositoryInterface(ABC):
    @abstractmethod
    async def get_all(self) -> List[CustomerIncidentPrediction]:
        pass
    
    @abstractmethod
    async def get_by_id(self, prediction_id: int) -> Optional[CustomerIncidentPrediction]:
        pass
    
    @abstractmethod
    async def get_by_customer_id(self, customer_id: str) -> Optional[CustomerIncidentPrediction]:
        pass
    
    @abstractmethod
    async def get_by_region(self, client_region: str) -> List[CustomerIncidentPrediction]:
        pass
    
    @abstractmethod
    async def get_by_incident_type(self, incident_type: IncidentType) -> List[CustomerIncidentPrediction]:
        pass
    
    @abstractmethod
    async def get_by_risk_level(self, min_avg_risk: float) -> List[CustomerIncidentPrediction]:
        pass
    
    @abstractmethod
    async def create(self, prediction: CustomerIncidentPrediction) -> CustomerIncidentPrediction:
        pass
    
    @abstractmethod
    async def batch_create(self, predictions: List[CustomerIncidentPrediction]) -> List[CustomerIncidentPrediction]:
        pass
    
    @abstractmethod
    async def update(self, prediction_id: int, prediction: CustomerIncidentPrediction) -> Optional[CustomerIncidentPrediction]:
        pass
    
    @abstractmethod
    async def delete(self, prediction_id: int) -> bool:
        pass 