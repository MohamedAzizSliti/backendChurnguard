from domain.repositories.interaction_repository_interface import InteractionRepositoryInterface
from domain.entities.interaction import Interaction
from supabase import Client as SupabaseClient
from typing import List, Optional
from datetime import datetime
import uuid

class InteractionRepository(InteractionRepositoryInterface):
    def __init__(self, supabase: SupabaseClient):
        self.supabase = supabase
        self.table = "interactions"
    
    async def get_by_client_id(self, client_id: str) -> List[Interaction]:
        response = self.supabase.table(self.table).select("*").eq("clientId", client_id).execute()
        data = response.data or []
        return [Interaction.from_dict(item) for item in data]
    
    async def create(self, interaction: Interaction) -> Interaction:
        if not interaction.id:
            interaction.id = str(uuid.uuid4())
        interaction.created_at = datetime.now()
        interaction_dict = interaction.to_dict()
        self.supabase.table(self.table).insert(interaction_dict).execute()
        return interaction
    
    async def delete(self, interaction_id: str) -> bool:
        self.supabase.table(self.table).delete().eq("id", interaction_id).execute()
        return True
