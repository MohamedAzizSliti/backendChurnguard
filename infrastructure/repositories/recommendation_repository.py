from domain.repositories.recommendation_repository_interface import RecommendationRepositoryInterface
from domain.entities.recommendation import Recommendation
from supabase import Client as SupabaseClient
from typing import List, Optional
from datetime import datetime
import uuid

class RecommendationRepository(RecommendationRepositoryInterface):
    def __init__(self, supabase: SupabaseClient):
        self.supabase = supabase
        self.table = "recommendations"
    
    async def get_by_client_id(self, client_id: str) -> List[Recommendation]:
        response = self.supabase.table(self.table).select("*").eq("clientId", client_id).execute()
        data = response.data or []
        return [Recommendation.from_dict(item) for item in data]
    
    async def create(self, recommendation: Recommendation) -> Recommendation:
        if not recommendation.id:
            recommendation.id = str(uuid.uuid4())
        recommendation.created_at = datetime.now()
        recommendation_dict = recommendation.to_dict()
        self.supabase.table(self.table).insert(recommendation_dict).execute()
        return recommendation
    
    async def delete(self, recommendation_id: str) -> bool:
        self.supabase.table(self.table).delete().eq("id", recommendation_id).execute()
        return True
