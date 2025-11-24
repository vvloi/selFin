"""Transaction model."""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.db.base import Base


class TransactionType(str, Enum):
    """Transaction type enumeration."""
    EXPENSE = "EXPENSE"
    INCOME = "INCOME"
    TRANSFER = "TRANSFER"


class Transaction(Base):
    """Transaction entity for tracking financial activities."""
    
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(SQLEnum(TransactionType), nullable=False, index=True)
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    currency = Column(String, nullable=False, default="VND")
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), index=True)
    to_wallet_id = Column(Integer, ForeignKey("wallets.id"), index=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    wallet = relationship("Wallet", foreign_keys=[wallet_id], back_populates="transactions_from")
    to_wallet = relationship("Wallet", foreign_keys=[to_wallet_id], back_populates="transactions_to")
