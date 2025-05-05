from domain.entities.user import User
from domain.value_objects.auth_token import AuthToken
from domain.repositories.user_repository_interface import UserRepositoryInterface
from application.dtos.auth_dtos import UserCreateDTO, UserLoginDTO, TokenResponseDTO, UserProfileDTO
from infrastructure.services.jwt_service import JWTService
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from supabase import Client as SupabaseClient
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthApplicationService:
    def __init__(
        self, 
        user_repository: UserRepositoryInterface,
        jwt_service: JWTService,
        supabase: SupabaseClient
    ):
        self.user_repository = user_repository
        self.jwt_service = jwt_service
        self.supabase = supabase
    
    async def register_user(self, user_data: UserCreateDTO) -> TokenResponseDTO:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = await self.user_repository.get_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Hash the password
            hashed_password = pwd_context.hash(user_data.password)
            
            # Create user in our domain
            user = User(
                id=None,  # Supabase will generate the ID
                email=user_data.email,
                full_name=user_data.full_name,
                role=user_data.role,
                password=hashed_password,
                created_at=datetime.now()
            )
            
            # Save user to repository (Supabase)
            created_user = await self.user_repository.create(user)
            
            # Generate JWT token
            token = self.jwt_service.create_access_token({"sub": created_user.id})
            
            return TokenResponseDTO(
                access_token=token,
                token_type="bearer",
                user_id=created_user.id,
                email=created_user.email,
                full_name=created_user.full_name,
                role=created_user.role.value
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration failed: {str(e)}"
            )
    
    async def login_user(self, login_data: UserLoginDTO) -> TokenResponseDTO:
        """Login a user"""
        try:
            # Get user from repository (Supabase)
            user = await self.user_repository.get_by_email(login_data.email)
            if not user or not pwd_context.verify(login_data.password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Generate JWT token
            token = self.jwt_service.create_access_token({"sub": user.id})
            
            return TokenResponseDTO(
                access_token=token,
                token_type="bearer",
                user_id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role.value
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def get_current_user(self, user_id: str) -> UserProfileDTO:
        """Get current user profile"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserProfileDTO(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            created_at=user.created_at.isoformat() if user.created_at else None
        )
