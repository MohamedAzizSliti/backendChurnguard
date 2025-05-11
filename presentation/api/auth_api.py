from fastapi import APIRouter, Depends, HTTPException, status, Path, Body
from fastapi.security import OAuth2PasswordBearer
from application.services.auth_service import AuthApplicationService
from application.dtos.auth_dtos import UserCreateDTO, UserLoginDTO, TokenResponseDTO, UserProfileDTO, UserListDTO, UserUpdateDTO
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.services.jwt_service import JWTService
from infrastructure.services.supabase_initializer import get_supabase_client
import jwt
from pydantic import BaseModel

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Services
supabase_client = get_supabase_client()
user_repository = UserRepository(supabase_client)
jwt_service = JWTService()
auth_service = AuthApplicationService(user_repository, jwt_service, supabase_client)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserProfileDTO:
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt_service.decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    return await auth_service.get_current_user(user_id)

@router.post("/register", response_model=TokenResponseDTO)
async def register_user(user: UserCreateDTO):
    """Register a new user"""
    return await auth_service.register_user(user)

@router.post("/login", response_model=TokenResponseDTO)
async def login_user(user: UserLoginDTO):
    """Login a user"""
    return await auth_service.login_user(user)

@router.get("/me", response_model=UserProfileDTO)
async def read_users_me(current_user: UserProfileDTO = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.get("/users", response_model=UserListDTO)
async def get_all_users(current_user: UserProfileDTO = Depends(get_current_user)):
    """Get all users (admin only)"""
    return await auth_service.get_all_users(current_user)

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str = Path(..., title="The ID of the user to delete"),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Delete a user (admin only)"""
    return await auth_service.delete_user(user_id, current_user)

@router.put("/users/{user_id}", response_model=UserProfileDTO)
async def update_user(
    user_id: str = Path(..., title="The ID of the user to update"),
    user_data: UserUpdateDTO = None,
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Update a user (admin only)"""
    return await auth_service.update_user(user_id, user_data, current_user)

@router.post("/users", response_model=TokenResponseDTO)
async def create_user(
    user: UserCreateDTO,
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Create a new user (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create users"
        )
    try:
        return await auth_service.register_user(user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@router.put("/users/me", response_model=UserProfileDTO)
async def update_self(
    user_data: UserUpdateDTO = Body(...),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Update own profile data (authenticated user)"""
    return await auth_service.update_self(current_user.id, user_data)

class PasswordChangeDTO(BaseModel):
    current_password: str
    new_password: str

@router.put("/users/me/password")
async def change_password(
    passwords: PasswordChangeDTO = Body(...),
    current_user: UserProfileDTO = Depends(get_current_user)
):
    """Change own password (authenticated user)"""
    return await auth_service.change_password(current_user.id, passwords.current_password, passwords.new_password)
