from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.note import Note

class NoteRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_id(self, note_id: str) -> Optional[Note]:
        pass
    
    @abstractmethod
    async def get_by_sender_id(self, sender_id: str) -> List[Note]:
        pass
    
    @abstractmethod
    async def get_by_recipient(self, role: str) -> List[Note]:
        pass
    
    @abstractmethod
    async def get_by_recipient_for_user(self, user_id: str, role: str) -> List[Note]:
        """Get notes where the user is a recipient based on their role"""
        pass
    
    @abstractmethod
    async def create(self, note: Note) -> Note:
        pass
    
    @abstractmethod
    async def update(self, note: Note) -> Note:
        pass
    
    @abstractmethod
    async def delete(self, note_id: str) -> bool:
        pass
    
    @abstractmethod
    async def mark_as_read(self, note_id: str) -> bool:
        pass 