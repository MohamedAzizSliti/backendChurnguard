from domain.repositories.user_repository_interface import UserRepositoryInterface
from domain.entities.user import User
from supabase import Client
from typing import List, Optional
from datetime import datetime

class UserRepository(UserRepositoryInterface):
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = "users"
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        response = self.supabase.table(self.table).select("*").eq("id", user_id).execute()
        data = response.data
        if not data:
            return None
        return User.from_dict(data[0])
    
    async def get_by_email(self, email: str) -> Optional[User]:
        response = self.supabase.table(self.table).select("*").eq("email", email).execute()
        data = response.data
        if not data:
            return None
        return User.from_dict(data[0])
    

    async def create(self, user: User) -> User:
                # 1. Stamp creation time
                user.created_at = datetime.now()
                user.updated_at = None
                # 2. Build payload WITHOUT the id field
                payload = user.to_dict()
                payload.pop("id", None)
                # 3. Insert & return the full row (including generated id)
                response = self.supabase.table(self.table) \
                    .insert(payload, returning="representation") \
                    .execute()
                inserted_rows = response.data or []
                if not inserted_rows:
                    raise Exception("Failed to insert user")
                # 4. Pull the generated id back onto the domain user
                user.id = inserted_rows[0]["id"]
                return user
    
    async def update(self, user: User) -> User:
        user.updated_at = datetime.now()
        user_dict = user.to_dict()
        self.supabase.table(self.table).update(user_dict).eq("id", user.id).execute()
        return user
    
    async def delete(self, user_id: str) -> bool:
        self.supabase.table(self.table).delete().eq("id", user_id).execute()
        return True
