from fastapi import APIRouter, Depends, Path, HTTPException, status
from application.services.note_service import NoteApplicationService
from application.dtos.auth_dtos import UserProfileDTO
from application.dtos.note_dtos import NoteCreateDTO, NoteResponseDTO, NoteBriefDTO
from infrastructure.repositories.note_repository import NoteRepository
from presentation.api.auth_api import get_current_user
from typing import List
from infrastructure.services.supabase_initializer import get_supabase_client

router = APIRouter()

# Supabase client
supabase_client = get_supabase_client()

# Repositories
note_repository = NoteRepository(supabase_client)

# Services
note_service = NoteApplicationService(note_repository)

@router.post("/", response_model=NoteResponseDTO)
async def create_note(
    note_data: NoteCreateDTO,
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Create a new note"""
    return await note_service.create_note(note_data, current_user.id, current_user.role)

@router.get("/inbox", response_model=List[NoteResponseDTO])
async def get_received_notes(current_user: UserProfileDTO = Depends(get_current_user)):
    """Get notes received by the current user"""
    return await note_service.get_received_notes(current_user.id, current_user.role)

@router.get("/sent", response_model=List[NoteResponseDTO])
async def get_sent_notes(current_user: UserProfileDTO = Depends(get_current_user)):
    """Get notes sent by the current user"""
    return await note_service.get_sent_notes(current_user.id)

@router.get("/{note_id}", response_model=NoteResponseDTO)
async def get_note(
    note_id: str = Path(..., title="The ID of the note to get"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Get a specific note by ID"""
    return await note_service.get_note_by_id(note_id, current_user.id, current_user.role)

@router.post("/{note_id}/read", response_model=bool)
async def mark_note_as_read(
    note_id: str = Path(..., title="The ID of the note to mark as read"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Mark a note as read"""
    return await note_service.mark_as_read(note_id, current_user.id, current_user.role) 