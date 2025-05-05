from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from domain.entities.user import UserRole

class UserCreateDTO(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.USER
    
    @validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str

class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str
    full_name: str
    role: str

class UserProfileDTO(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    created_at: Optional[str] = None
