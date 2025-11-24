"""Budget router."""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.schemas.budget import (
    BudgetCreateRequest, BudgetUpdateRequest, BudgetResponse, BudgetSummaryResponse, PeriodType
)
from app.services.budget_service import budget_service
from app.api.v1.deps import get_current_user
from app.models.user import User


router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("", response_model=list[BudgetResponse])
def get_budgets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all budgets for current user."""
    budgets = budget_service.get_all_budgets(db, current_user.id)
    return budgets


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    request: BudgetCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new budget."""
    from app.models.budget import PeriodType as ModelPeriodType
    
    budget = budget_service.create_budget(
        db, current_user.id, request.category_id, request.amount_limit,
        ModelPeriodType(request.period_type.value), request.start_date, request.end_date
    )
    return budget


@router.get("/summary", response_model=BudgetSummaryResponse)
def get_budget_summary(
    year: int = Query(...),
    month: Optional[int] = Query(None),
    quarter: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get budget summary for a period."""
    summary = budget_service.get_budget_summary(db, current_user.id, year, month, quarter)
    return summary


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get budget by ID."""
    budget = budget_service.get_budget_by_id(db, budget_id, current_user.id)
    return budget


@router.patch("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    request: BudgetUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update budget."""
    from app.models.budget import PeriodType as ModelPeriodType
    
    model_period = ModelPeriodType(request.period_type.value) if request.period_type else None
    
    budget = budget_service.update_budget(
        db, budget_id, current_user.id, request.amount_limit,
        model_period, request.start_date, request.end_date
    )
    return budget


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete budget."""
    budget_service.delete_budget(db, budget_id, current_user.id)
    return None
