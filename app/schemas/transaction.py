"""Transaction schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from app.schemas.user import WalletResponse


class TransactionType(str, Enum):
    """Transaction type."""
    EXPENSE = "EXPENSE"
    INCOME = "INCOME"
    TRANSFER = "TRANSFER"


class CategoryType(str, Enum):
    """Category type."""
    EXPENSE = "EXPENSE"
    INCOME = "INCOME"


class CategoryCreateRequest(BaseModel):
    """Category creation request."""
    name: str
    type: CategoryType
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryResponse(BaseModel):
    """Category response."""
    id: int
    user_id: int
    name: str
    type: str
    icon: Optional[str] = None
    color: Optional[str] = None
    
    class Config:
        from_attributes = True


class TransactionCreateRequest(BaseModel):
    """Transaction creation request."""
    type: TransactionType
    amount: float = Field(gt=0)
    currency: str = "VND"
    date: datetime
    category_id: Optional[int] = None
    wallet_id: Optional[int] = None
    to_wallet_id: Optional[int] = None
    description: Optional[str] = None


class TransactionUpdateRequest(BaseModel):
    """Transaction update request."""
    type: Optional[TransactionType] = None
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = None
    date: Optional[datetime] = None
    category_id: Optional[int] = None
    wallet_id: Optional[int] = None
    to_wallet_id: Optional[int] = None
    description: Optional[str] = None


class TransactionResponse(BaseModel):
    """Transaction response."""
    id: int
    user_id: int
    type: str
    amount: float
    currency: str
    date: datetime
    category_id: Optional[int] = None
    category: Optional[CategoryResponse] = None
    wallet_id: Optional[int] = None
    wallet: Optional['WalletResponse'] = None
    to_wallet_id: Optional[int] = None
    to_wallet: Optional['WalletResponse'] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Transaction list response with pagination."""
    items: list[TransactionResponse]
    total: int
    page: int
    size: int
    pages: int


class DailyTransactionGroup(BaseModel):
    """Daily transaction group."""
    date: str
    total_income: float
    total_expense: float
    total_amount: float = 0.0
    transaction_count: int = 0
    transactions: list[TransactionResponse]


class WeeklyTransactionGroup(BaseModel):
    """Weekly transaction group."""
    year: int
    week: int
    start_date: str
    end_date: str
    total_income: float
    total_expense: float
    total_amount: float = 0.0
    transaction_count: int = 0
    transactions: list[TransactionResponse]


class MonthlyTransactionGroup(BaseModel):
    """Monthly transaction group."""
    year: int
    month: int
    total_income: float
    total_expense: float
    transactions: list[TransactionResponse]


# Resolve forward references
def _rebuild_models():
    """Rebuild models with forward references."""
    try:
        from app.schemas.user import WalletResponse
        TransactionResponse.model_rebuild()
    except Exception:
        pass

_rebuild_models()
