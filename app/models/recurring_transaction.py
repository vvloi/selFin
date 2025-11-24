"""Recurring transaction model."""
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Enum as SQLEnum, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.db.base import Base


class Frequency(str, Enum):
    """Recurring transaction frequency enumeration."""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class RecurringTransaction(Base):
    """Recurring transaction entity for automated recurring expenses/income."""
    
    __tablename__ = "recurring_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String, nullable=False)  # EXPENSE, INCOME, TRANSFER
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    currency = Column(String, nullable=False, default="VND")
    category_id = Column(Integer, ForeignKey("categories.id"), index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), index=True)
    to_wallet_id = Column(Integer, ForeignKey("wallets.id"), index=True)
    description = Column(Text)
    frequency = Column(SQLEnum(Frequency), nullable=False)
    start_date = Column(Date, nullable=False)
    next_run_date = Column(Date, nullable=False, index=True)
    last_run_date = Column(Date)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="recurring_transactions")
    category = relationship("Category", back_populates="recurring_transactions")
    wallet = relationship("Wallet", foreign_keys=[wallet_id], back_populates="recurring_transactions_from")
    to_wallet = relationship("Wallet", foreign_keys=[to_wallet_id], back_populates="recurring_transactions_to")
