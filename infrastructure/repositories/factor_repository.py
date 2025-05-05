from domain.repositories.factor_repository_interface import FactorRepositoryInterface
from domain.entities.factor import Factor
from supabase import Client as SupabaseClient
from typing import List, Optional
from datetime import datetime
import uuid

class FactorRepository(FactorRepositoryInterface):
    def __init__(self, supabase: SupabaseClient):
        self.supabase = supabase
        self.table = "factors"
    
    async def get_by_client_id(self, client_id: str) -> List[Factor]:
        response = self.supabase.table(self.table).select("*").eq("clientId", client_id).execute()
        data = response.data or []
        return [Factor.from_dict(item) for item in data]
    
    async def create(self, factor: Factor) -> Factor:
        if not factor.id:
            factor.id = str(uuid.uuid4())
        factor.created_at = datetime.now()
        factor_dict = factor.to_dict()
        self.supabase.table(self.table).insert(factor_dict).execute()
        return factor
    
    async def delete(self, factor_id: str) -> bool:
        self.supabase.table(self.table).delete().eq("id", factor_id).execute()
        return True
