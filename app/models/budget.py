"""Budget model."""
from sqlalchemy import Column, Integer, Numeric, DateTime, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.db.base import Base


class PeriodType(str, Enum):
    """Budget period type enumeration."""
    MONTHLY = "MONTHLY"
    WEEKLY = "WEEKLY"
    CUSTOM = "CUSTOM"


class Budget(Base):
    """Budget entity for expense tracking and limits."""
    
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    amount_limit = Column(Numeric(precision=15, scale=2), nullable=False)
    period_type = Column(SQLEnum(PeriodType), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")
