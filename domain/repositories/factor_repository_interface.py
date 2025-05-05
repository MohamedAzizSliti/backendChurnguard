from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.factor import Factor

class FactorRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_client_id(self, client_id: str) -> List[Factor]:
        pass
    
    @abstractmethod
    async def create(self, factor: Factor) -> Factor:
        pass
    
    @abstractmethod
    async def delete(self, factor_id: str) -> bool:
        pass
