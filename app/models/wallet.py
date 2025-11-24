"""Wallet model."""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Wallet(Base):
    """Wallet entity for managing accounts."""
    
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    currency = Column(String, nullable=False, default="VND")
    balance = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="wallets")
    transactions_from = relationship(
        "Transaction", 
        foreign_keys="Transaction.wallet_id",
        back_populates="wallet"
    )
    transactions_to = relationship(
        "Transaction",
        foreign_keys="Transaction.to_wallet_id",
        back_populates="to_wallet"
    )
    recurring_transactions_from = relationship(
        "RecurringTransaction",
        foreign_keys="RecurringTransaction.wallet_id",
        back_populates="wallet"
    )
    recurring_transactions_to = relationship(
        "RecurringTransaction",
        foreign_keys="RecurringTransaction.to_wallet_id",
        back_populates="to_wallet"
    )
