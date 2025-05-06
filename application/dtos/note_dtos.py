from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class NoteCreateDTO(BaseModel):
    title: str
    description: str
    recipients: List[str]

class NoteUpdateDTO(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    recipients: Optional[List[str]] = None

class NoteResponseDTO(BaseModel):
    id: str
    title: str
    description: str
    sender_id: str
    recipients: List[str]
    is_read: bool
    timestamp: str

class NoteBriefDTO(BaseModel):
    id: str
    title: str
    sender_id: str
    is_read: bool
    timestamp: str 