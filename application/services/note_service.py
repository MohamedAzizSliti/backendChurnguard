from domain.entities.note import Note
from domain.repositories.note_repository_interface import NoteRepositoryInterface
from application.dtos.note_dtos import NoteCreateDTO, NoteUpdateDTO, NoteResponseDTO, NoteBriefDTO
from domain.entities.user import UserRole
from fastapi import HTTPException, status
from typing import List
from datetime import datetime

class NoteApplicationService:
    def __init__(self, note_repository: NoteRepositoryInterface):
        self.note_repository = note_repository
    
    async def create_note(self, note_data: NoteCreateDTO, sender_id: str, sender_role: str) -> NoteResponseDTO:
        """Create a new note
        
        Only Admins can send notes to any role.
        Other roles can only send notes to Admins.
        """
        try:
            # If sender is not Admin, validate recipients to ensure they can only send to Admins
            if sender_role != UserRole.ADMIN.value:
                # Non-admin users can only send to admins
                if any(recipient != UserRole.ADMIN.value for recipient in note_data.recipients):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You can only send notes to administrators"
                    )
            
            # Create the note
            note = Note(
                id=None,  # Will be generated
                title=note_data.title,
                description=note_data.description,
                sender_id=sender_id,
                recipients=note_data.recipients,
                is_read=False,
                timestamp=datetime.now()
            )
            
            # Save note to repository
            created_note = await self.note_repository.create(note)
            
            # Convert to response DTO
            return NoteResponseDTO(
                id=created_note.id,
                title=created_note.title,
                description=created_note.description,
                sender_id=created_note.sender_id,
                recipients=created_note.recipients,
                is_read=created_note.is_read,
                timestamp=created_note.timestamp.isoformat()
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Note creation failed: {str(e)}"
            )
    
    async def get_received_notes(self, user_id: str, user_role: str) -> List[NoteResponseDTO]:
        """Get notes received by the current user based on their role"""
        try:
            notes = await self.note_repository.get_by_recipient(user_role)
            return [
                NoteResponseDTO(
                    id=note.id,
                    title=note.title,
                    description=note.description,
                    sender_id=note.sender_id,
                    recipients=note.recipients,
                    is_read=note.is_read,
                    timestamp=note.timestamp.isoformat()
                ) for note in notes
            ]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to retrieve notes: {str(e)}"
            )
    
    async def get_sent_notes(self, user_id: str) -> List[NoteResponseDTO]:
        """Get notes sent by the current user"""
        try:
            notes = await self.note_repository.get_by_sender_id(user_id)
            return [
                NoteResponseDTO(
                    id=note.id,
                    title=note.title,
                    description=note.description,
                    sender_id=note.sender_id,
                    recipients=note.recipients,
                    is_read=note.is_read,
                    timestamp=note.timestamp.isoformat()
                ) for note in notes
            ]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to retrieve sent notes: {str(e)}"
            )
    
    async def get_note_by_id(self, note_id: str, user_id: str, user_role: str) -> NoteResponseDTO:
        """Get a specific note by ID, ensuring the user has access to it"""
        try:
            note = await self.note_repository.get_by_id(note_id)
            if not note:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Note not found"
                )
            
            # Check if user has access to this note (either as sender or recipient)
            if note.sender_id != user_id and user_role not in note.recipients:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to view this note"
                )
            
            return NoteResponseDTO(
                id=note.id,
                title=note.title,
                description=note.description,
                sender_id=note.sender_id,
                recipients=note.recipients,
                is_read=note.is_read,
                timestamp=note.timestamp.isoformat()
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to retrieve note: {str(e)}"
            )
    
    async def mark_as_read(self, note_id: str, user_id: str, user_role: str) -> bool:
        """Mark a note as read"""
        try:
            # First verify the user has access to this note
            note = await self.get_note_by_id(note_id, user_id, user_role)
            
            # Now mark it as read
            result = await self.note_repository.mark_as_read(note_id)
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to mark note as read: {str(e)}"
            ) 