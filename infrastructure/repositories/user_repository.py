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
    
    async def get_by_cin(self, cin: str) -> Optional[User]:
        response = self.supabase.table(self.table).select("*").eq("cin", cin).execute()
        data = response.data
        if not data:
            return None
        return User.from_dict(data[0])
    
    async def get_by_code(self, code: str) -> Optional[User]:
        response = self.supabase.table(self.table).select("*").eq("code", code).execute()
        data = response.data
        if not data:
            return None
        return User.from_dict(data[0])
    
    async def get_all(self) -> List[User]:
        response = self.supabase.table(self.table).select("*").execute()
        data = response.data
        return [User.from_dict(item) for item in data]
    
    async def create(self, user: User) -> User:
        try:
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
            
            if not response.data or len(response.data) == 0:
                raise Exception("Failed to insert user: No data returned from database")
            
            # 4. Pull the generated id back onto the domain user
            inserted_data = response.data[0]
            if not inserted_data.get("id"):
                raise Exception("Failed to insert user: No ID returned from database")
                
            user.id = inserted_data["id"]
            return user
            
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")
    
    async def update(self, user: User) -> User:
        user.updated_at = datetime.now()
        user_dict = user.to_dict()
        self.supabase.table(self.table).update(user_dict).eq("id", user.id).execute()
        return user
    
    async def delete(self, user_id: str) -> bool:
        self.supabase.table(self.table).delete().eq("id", user_id).execute()
        return True
