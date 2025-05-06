from fastapi import APIRouter, Depends, Path
from application.services.client_service import ClientApplicationService
from application.dtos.auth_dtos import UserProfileDTO
from application.dtos.client_dtos import ClientDTO, ClientDetailDTO, ClientCreateDTO
from infrastructure.repositories.client_repository import ClientRepository
from infrastructure.repositories.interaction_repository import InteractionRepository
from infrastructure.repositories.recommendation_repository import RecommendationRepository
from infrastructure.repositories.factor_repository import FactorRepository
from presentation.api.auth_api import get_current_user
from typing import List
from infrastructure.services.supabase_initializer import get_supabase_client

router = APIRouter()

# Supabase client
supabase_client = get_supabase_client()

# Repositories
client_repository = ClientRepository(supabase_client)
interaction_repository = InteractionRepository(supabase_client)
recommendation_repository = RecommendationRepository(supabase_client)
factor_repository = FactorRepository(supabase_client)

# Services
client_service = ClientApplicationService(
    client_repository,  
    interaction_repository, 
    recommendation_repository, 
    factor_repository
)

@router.get("/", response_model=List[ClientDTO])
async def get_clients(current_user: UserProfileDTO = Depends(get_current_user)):
    """Get all clients"""
    return await client_service.get_all_clients()

@router.get("/{client_id}/detail", response_model=ClientDetailDTO)
async def get_client_detail(
    client_id: str = Path(..., title="The ID of the client to get detailed information for"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Get detailed client information by ID"""
    return await client_service.get_client_detail(client_id)

@router.put("/{client_id}", response_model=ClientDTO)
async def update_client(
    client: ClientCreateDTO,
    client_id: str = Path(..., title="The ID of the client to update"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Update a client by ID"""
    return await client_service.update_client(client_id, client)

@router.get("/{client_id}", response_model=ClientDTO)
async def get_client(
    client_id: str = Path(..., title="The ID of the client to get"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Get client by ID"""
    return await client_service.get_client_by_id(client_id)

@router.post("/", response_model=ClientDTO)
async def create_client(
    client: ClientCreateDTO,
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Create a new client"""
    return await client_service.create_client(client)
