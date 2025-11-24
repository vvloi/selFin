"""Analytics schemas."""
from pydantic import BaseModel
from typing import Optional


class CategorySpendingResponse(BaseModel):
    """Category spending response."""
    category_id: int
    category_name: str
    total_amount: float
    percentage: float
    transaction_count: int


class SpendingTrendResponse(BaseModel):
    """Spending trend response."""
    period: str
    year: int
    month: Optional[int] = None
    week: Optional[int] = None
    day: Optional[str] = None
    total_expense: float
    total_income: float


class TopCategoryResponse(BaseModel):
    """Top category response."""
    category_id: int
    category_name: str
    total_amount: float
    transaction_count: int
