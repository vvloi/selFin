"""Authentication service for business logic."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta
from typing import Tuple
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.repositories.user_repository import user_repository
from app.repositories.wallet_repository import wallet_repository
from app.models.user import User


class AuthService:
    """Service for authentication and user management business logic."""
    
    def register_user(self, db: Session, email: str, password: str, full_name: str) -> User:
        """Register a new user with validation."""
        if user_repository.exists_by_email(db, email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        
        self._validate_password(password)
        
        hashed_password = hash_password(password)
        user = user_repository.create(db, email, hashed_password, full_name)
        
        self._create_default_wallet(db, user.id)
        
        return user
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Tuple[str, User]:
        """Authenticate user and return access token."""
        user = user_repository.get_by_email(db, email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        
        return access_token, user
    
    def get_current_user(self, db: Session, user_id: int) -> User:
        """Get current authenticated user."""
        user = user_repository.get_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    
    def _validate_password(self, password: str) -> None:
        """Validate password strength."""
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
    
    def _create_default_wallet(self, db: Session, user_id: int) -> None:
        """Create default wallet for new user."""
        wallet_repository.create(db, user_id, "Default Wallet", "VND", 0.0)


auth_service = AuthService()
