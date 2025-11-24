"""Authentication and user schemas."""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserRegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str
    full_name: str


class UserLoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response."""
    id: int
    email: str
    full_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class WalletCreateRequest(BaseModel):
    """Wallet creation request."""
    name: str
    currency: str = "VND"
    initial_balance: float = 0.0


class WalletUpdateRequest(BaseModel):
    """Wallet update request."""
    name: Optional[str] = None
    currency: Optional[str] = None


class WalletResponse(BaseModel):
    """Wallet response."""
    id: int
    user_id: int
    name: str
    currency: str
    balance: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
