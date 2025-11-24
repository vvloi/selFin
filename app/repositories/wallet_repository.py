"""Wallet repository for database operations."""
from sqlalchemy.orm import Session
from typing import Optional, List
from decimal import Decimal
from app.models.wallet import Wallet


class WalletRepository:
    """Repository for Wallet entity database operations."""
    
    def create(self, db: Session, user_id: int, name: str, currency: str, initial_balance: float) -> Wallet:
        """Create a new wallet."""
        wallet = Wallet(
            user_id=user_id,
            name=name,
            currency=currency,
            balance=Decimal(str(initial_balance))
        )
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        return wallet
    
    def get_by_id(self, db: Session, wallet_id: int, user_id: int) -> Optional[Wallet]:
        """Get wallet by ID for a specific user."""
        return db.query(Wallet).filter(
            Wallet.id == wallet_id,
            Wallet.user_id == user_id
        ).first()
    
    def get_all_by_user(self, db: Session, user_id: int) -> List[Wallet]:
        """Get all wallets for a user."""
        return db.query(Wallet).filter(Wallet.user_id == user_id).all()
    
    def update(self, db: Session, wallet: Wallet) -> Wallet:
        """Update wallet."""
        db.commit()
        db.refresh(wallet)
        return wallet
    
    def delete(self, db: Session, wallet: Wallet) -> None:
        """Delete wallet."""
        db.delete(wallet)
        db.commit()
    
    def update_balance(self, db: Session, wallet_id: int, amount_delta: Decimal) -> None:
        """Update wallet balance by delta amount."""
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if wallet:
            wallet.balance += amount_delta
            db.commit()


wallet_repository = WalletRepository()
