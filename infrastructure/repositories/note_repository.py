from domain.repositories.note_repository_interface import NoteRepositoryInterface
from domain.entities.note import Note
from supabase import Client
from typing import List, Optional
from datetime import datetime

class NoteRepository(NoteRepositoryInterface):
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = "notes"
    
    async def get_by_id(self, note_id: str) -> Optional[Note]:
        response = self.supabase.table(self.table).select("*").eq("id", note_id).execute()
        data = response.data
        if not data:
            return None
        return Note.from_dict(data[0])
    
    async def get_by_sender_id(self, sender_id: str) -> List[Note]:
        response = self.supabase.table(self.table).select("*").eq("sender_id", sender_id).execute()
        data = response.data
        return [Note.from_dict(item) for item in data]
    
    async def get_by_recipient(self, role: str) -> List[Note]:
        # Use ?in Supabase operator to check if role is in the recipients array
        response = self.supabase.table(self.table).select("*").contains("recipients", [role]).execute()
        data = response.data
        return [Note.from_dict(item) for item in data]
    
    async def get_by_recipient_for_user(self, user_id: str, role: str) -> List[Note]:
        """Get notes where the user is a recipient based on their role"""
        # First, get all notes for this role
        notes_for_role = await self.get_by_recipient(role)
        # Return all notes for that role (user will filter by their role)
        return notes_for_role
    
    async def create(self, note: Note) -> Note:
        # Stamp creation time
        note.timestamp = datetime.now()
        # Build payload WITHOUT the id field
        payload = note.to_dict()
        payload.pop("id", None)
        # Insert & return the full row (including generated id)
        response = self.supabase.table(self.table) \
            .insert(payload, returning="representation") \
            .execute()
        inserted_rows = response.data or []
        if not inserted_rows:
            raise Exception("Failed to insert note")
        # Pull the generated id back onto the domain note
        note.id = inserted_rows[0]["id"]
        return note
    
    async def update(self, note: Note) -> Note:
        note_dict = note.to_dict()
        self.supabase.table(self.table).update(note_dict).eq("id", note.id).execute()
        return note
    
    async def delete(self, note_id: str) -> bool:
        self.supabase.table(self.table).delete().eq("id", note_id).execute()
        return True
    
    async def mark_as_read(self, note_id: str) -> bool:
        self.supabase.table(self.table).update({"is_read": True}).eq("id", note_id).execute()
        return True 