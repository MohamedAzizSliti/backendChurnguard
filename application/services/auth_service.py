from domain.entities.user import User, UserRole
from domain.value_objects.auth_token import AuthToken
from domain.repositories.user_repository_interface import UserRepositoryInterface
from application.dtos.auth_dtos import UserCreateDTO, UserLoginDTO, TokenResponseDTO, UserProfileDTO, UserListDTO, UserUpdateDTO
from infrastructure.services.jwt_service import JWTService
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from supabase import Client as SupabaseClient
from passlib.context import CryptContext
from typing import List

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
            
            # Check if CIN already exists
            existing_cin = await self.user_repository.get_by_cin(user_data.cin)
            if existing_cin:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CIN already registered"
                )
            
            # Check if code already exists
            existing_code = await self.user_repository.get_by_code(user_data.code)
            if existing_code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Code already registered"
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
                cin=user_data.cin,
                code=user_data.code,
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
                role=created_user.role.value,
                cin=created_user.cin,
                code=created_user.code
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
                role=user.role.value,
                cin=user.cin,
                code=user.code
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
            cin=user.cin,
            code=user.code,
            created_at=user.created_at.isoformat() if user.created_at else None
        )
    
    async def get_all_users(self, current_user: UserProfileDTO) -> UserListDTO:
        """Get all users (admin only)"""
        if current_user.role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can access this endpoint"
            )
        
        users = await self.user_repository.get_all()
        return UserListDTO(users=[
            UserProfileDTO(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role.value,
                cin=user.cin,
                code=user.code,
                created_at=user.created_at.isoformat() if user.created_at else None
            ) for user in users
        ])
    
    async def delete_user(self, user_id: str, current_user: UserProfileDTO) -> bool:
        """Delete a user (admin only)"""
        if current_user.role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can delete users"
            )
        
        # Check if user exists
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent self-deletion
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        return await self.user_repository.delete(user_id)
    
    async def update_user(self, user_id: str, user_data: UserUpdateDTO, current_user: UserProfileDTO) -> UserProfileDTO:
        """Update a user (admin only)"""
        if current_user.role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update users"
            )
        
        # Check if user exists
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update user fields if provided
        if user_data.email is not None:
            # Check if new email is already taken
            existing_user = await self.user_repository.get_by_email(user_data.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            user.email = user_data.email
        
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.role is not None:
            user.role = user_data.role
        
        if user_data.cin is not None:
            # Check if new CIN is already taken
            existing_user = await self.user_repository.get_by_cin(user_data.cin)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CIN already registered"
                )
            user.cin = user_data.cin
        
        if user_data.code is not None:
            # Check if new code is already taken
            existing_user = await self.user_repository.get_by_code(user_data.code)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Code already registered"
                )
            user.code = user_data.code
        
        if user_data.password is not None:
            user.password = pwd_context.hash(user_data.password)
        
        # Update user in repository
        updated_user = await self.user_repository.update(user)
        
        return UserProfileDTO(
            id=updated_user.id,
            email=updated_user.email,
            full_name=updated_user.full_name,
            role=updated_user.role.value,
            cin=updated_user.cin,
            code=updated_user.code,
            created_at=updated_user.created_at.isoformat() if updated_user.created_at else None
        )
