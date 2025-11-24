"""Authentication router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import (
    UserRegisterRequest, UserLoginRequest, UserResponse,
    TokenResponse, WalletCreateRequest, WalletUpdateRequest, WalletResponse
)
from app.services.auth_service import auth_service
from app.repositories.wallet_repository import wallet_repository
from app.api.v1.deps import get_current_user
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["Auth"])
wallet_router = APIRouter(prefix="/wallets", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    user = auth_service.register_user(db, request.email, request.password, request.full_name)
    return user


@router.post("/login", response_model=TokenResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """Login user and return access token."""
    access_token, user = auth_service.authenticate_user(db, request.email, request.password)
    return TokenResponse(access_token=access_token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@wallet_router.get("", response_model=list[WalletResponse])
def get_wallets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all wallets for current user."""
    wallets = wallet_repository.get_all_by_user(db, current_user.id)
    return wallets


@wallet_router.post("", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
def create_wallet(
    request: WalletCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new wallet."""
    wallet = wallet_repository.create(
        db, current_user.id, request.name, request.currency, request.initial_balance
    )
    return wallet


@wallet_router.get("/{wallet_id}", response_model=WalletResponse)
def get_wallet(
    wallet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get wallet by ID."""
    wallet = wallet_repository.get_by_id(db, wallet_id, current_user.id)
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    return wallet


@wallet_router.patch("/{wallet_id}", response_model=WalletResponse)
def update_wallet(
    wallet_id: int,
    request: WalletUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update wallet."""
    wallet = wallet_repository.get_by_id(db, wallet_id, current_user.id)
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    
    if request.name is not None:
        wallet.name = request.name
    if request.currency is not None:
        wallet.currency = request.currency
    
    updated_wallet = wallet_repository.update(db, wallet)
    return updated_wallet


@wallet_router.delete("/{wallet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wallet(
    wallet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete wallet."""
    wallet = wallet_repository.get_by_id(db, wallet_id, current_user.id)
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    
    wallet_repository.delete(db, wallet)
    return None
