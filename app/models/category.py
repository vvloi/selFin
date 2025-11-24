"""Category model."""
from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum
from app.db.base import Base


class CategoryType(str, Enum):
    """Category type enumeration."""
    EXPENSE = "EXPENSE"
    INCOME = "INCOME"


class Category(Base):
    """Category entity for organizing transactions."""
    
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    type = Column(SQLEnum(CategoryType), nullable=False)
    icon = Column(String)
    color = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")
    recurring_transactions = relationship("RecurringTransaction", back_populates="category")
