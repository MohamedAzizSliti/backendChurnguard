from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.interaction import Interaction

class InteractionRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_client_id(self, client_id: str) -> List[Interaction]:
        pass
    
    @abstractmethod
    async def create(self, interaction: Interaction) -> Interaction:
        pass
    
    @abstractmethod
    async def delete(self, interaction_id: str) -> bool:
        pass
