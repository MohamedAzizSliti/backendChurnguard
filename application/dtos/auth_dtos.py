from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from domain.entities.user import UserRole

class UserCreateDTO(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.ADMIN
    cin: str
    code: str
    
    @validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
    
    @validator('cin')
    def cin_must_be_valid(cls, v):
        if not v or len(v) < 5:
            raise ValueError('CIN must be at least 5 characters')
        return v
    
    @validator('code')
    def code_must_be_valid(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Code must be at least 3 characters')
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
    cin: str
    code: str

class UserProfileDTO(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    cin: str
    code: str
    created_at: Optional[str] = None

class UserListDTO(BaseModel):
    users: List[UserProfileDTO]

class UserUpdateDTO(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    cin: Optional[str] = None
    code: Optional[str] = None
    password: Optional[str] = None

    @validator('password')
    def password_must_be_strong(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

    @validator('cin')
    def cin_must_be_valid(cls, v):
        if v is not None and len(v) < 5:
            raise ValueError('CIN must be at least 5 characters')
        return v

    @validator('code')
    def code_must_be_valid(cls, v):
        if v is not None and len(v) < 3:
            raise ValueError('Code must be at least 3 characters')
        return v
