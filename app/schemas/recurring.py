"""Recurring transaction schemas."""
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING
from enum import Enum
from app.schemas.transaction import CategoryResponse

if TYPE_CHECKING:
    from app.schemas.user import WalletResponse
from app.schemas.transaction import TransactionType, CategoryResponse


class Frequency(str, Enum):
    """Recurring frequency."""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class RecurringTransactionCreateRequest(BaseModel):
    """Recurring transaction creation request."""
    type: TransactionType
    amount: float = Field(gt=0)
    currency: str = "VND"
    category_id: Optional[int] = None
    wallet_id: Optional[int] = None
    to_wallet_id: Optional[int] = None
    description: Optional[str] = None
    frequency: Frequency
    start_date: date
    is_active: bool = True


class RecurringTransactionUpdateRequest(BaseModel):
    """Recurring transaction update request."""
    type: Optional[TransactionType] = None
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = None
    category_id: Optional[int] = None
    wallet_id: Optional[int] = None
    to_wallet_id: Optional[int] = None
    description: Optional[str] = None
    frequency: Optional[Frequency] = None
    start_date: Optional[date] = None
    is_active: Optional[bool] = None


class RecurringTransactionResponse(BaseModel):
    """Recurring transaction response."""
    id: int
    user_id: int
    type: str
    amount: float
    currency: str
    category_id: Optional[int] = None
    category: Optional[CategoryResponse] = None
    wallet_id: Optional[int] = None
    wallet: Optional['WalletResponse'] = None
    to_wallet_id: Optional[int] = None
    to_wallet: Optional['WalletResponse'] = None
    description: Optional[str] = None
    frequency: str
    start_date: date
    next_run_date: date
    last_run_date: Optional[date] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Resolve forward references  
def _rebuild_models():
    """Rebuild models with forward references."""
    try:
        from app.schemas.user import WalletResponse
        RecurringTransactionResponse.model_rebuild()
    except Exception:
        pass

_rebuild_models()
