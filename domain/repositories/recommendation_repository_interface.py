from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.recommendation import Recommendation

class RecommendationRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_client_id(self, client_id: str) -> List[Recommendation]:
        pass
    
    @abstractmethod
    async def create(self, recommendation: Recommendation) -> Recommendation:
        pass
    
    @abstractmethod
    async def delete(self, recommendation_id: str) -> bool:
        pass
