"""Budget schemas."""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from enum import Enum
from app.schemas.transaction import CategoryResponse


class PeriodType(str, Enum):
    """Budget period type."""
    MONTHLY = "MONTHLY"
    WEEKLY = "WEEKLY"
    CUSTOM = "CUSTOM"


class BudgetCreateRequest(BaseModel):
    """Budget creation request."""
    category_id: int
    amount_limit: float = Field(gt=0)
    alert_threshold: float = Field(default=80.0, ge=0, le=100)  # Warning threshold percentage
    period_type: PeriodType
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class BudgetUpdateRequest(BaseModel):
    """Budget update request."""
    amount_limit: Optional[float] = Field(None, gt=0)
    alert_threshold: Optional[float] = Field(None, ge=0, le=100)  # Warning threshold percentage
    period_type: Optional[PeriodType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class BudgetResponse(BaseModel):
    """Budget response with usage information."""
    id: int
    user_id: int
    category_id: int
    category: Optional[CategoryResponse] = None
    amount_limit: float
    alert_threshold: float  # User-defined warning threshold percentage
    period_type: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    used_amount: float
    remaining_amount: float
    usage_percentage: float
    is_near_limit: bool
    is_exceeded: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BudgetSummaryResponse(BaseModel):
    """Budget summary response."""
    period: str
    total_budget: float
    total_spent: float
    budgets: list[BudgetResponse]
