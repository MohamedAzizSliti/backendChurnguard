from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.client import Client

class ClientRepositoryInterface(ABC):
    @abstractmethod
    async def get_all(self) -> List[Client]:
        pass
    
    @abstractmethod
    async def get_by_id(self, client_id: str) -> Optional[Client]:
        pass
    
    @abstractmethod
    async def create(self, client: Client) -> Client:
        pass
    
    @abstractmethod
    async def update(self, client: Client) -> Client:
        pass
    
    @abstractmethod
    async def delete(self, client_id: str) -> bool:
        pass
