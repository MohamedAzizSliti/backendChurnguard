from domain.repositories.client_repository_interface import ClientRepositoryInterface
from domain.entities.client import Client, Contact
from supabase import Client as SupabaseClient
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class ClientRepository(ClientRepositoryInterface):
    def __init__(self, supabase: SupabaseClient):
        self.supabase = supabase
        self.table = "clients"
    
    async def get_all(self) -> List[Client]:
        response = self.supabase.table(self.table).select("*").execute()
        data = response.data or []
        return [Client.from_dict(item) for item in data]
    
    async def get_by_id(self, client_id: str) -> Optional[Client]:
        response = self.supabase.table(self.table).select("*").eq("id", client_id).execute()
        data = response.data
        if not data:
            return None
        return Client.from_dict(data[0])
    # e.g. in client_repository.py
    async def create_from_dict(self, data: dict) -> Client:
        response = self.supabase.table(self.table).insert(data).execute()
        return Client(**response.data[0])

    
    async def create(self, client: Client) -> Client:
        if not client.id:
            client.id = str(uuid.uuid4())
        client.created_at = datetime.now()
        client.updated_at = None
        client_dict = client.to_dict()
        self.supabase.table(self.table).insert(client_dict).execute()
        return client
    
    async def update(self, client_id: str, client: Client) -> Client:
        data = {
            "name": client.name,
            "segment": client.segment,
            "since": client.since,
            "churn_risk": client.churn_risk,
            "contacts": client.contacts.dict(),
            # any other fields…
        }
        resp = await self.supabase \
            .from_(self.table) \
            .update(data) \
            .eq("id", client_id) \
            .execute()

        updated = resp.data[0]
        return Client(
            id=updated["id"],
            name=updated["name"],
            segment=updated["segment"],
            churn_risk=updated["churn_risk"],
            since=updated["since"],
            contacts=Contact(**updated["contacts"]),
            # map other fields…
        )
    
    async def delete(self, client_id: str) -> bool:
        self.supabase.table(self.table).delete().eq("id", client_id).execute()
        return True
