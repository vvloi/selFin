"""Budget service for business logic."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Tuple
from app.models.budget import Budget, PeriodType
from app.repositories.budget_repository import budget_repository
from app.repositories.transaction_repository import transaction_repository
from app.repositories.category_repository import category_repository
from app.core.config import settings


class BudgetService:
    """Service for budget business logic."""
    
    def create_budget(
        self,
        db: Session,
        user_id: int,
        category_id: int,
        amount_limit: float,
        period_type: PeriodType,
        alert_threshold: float = 80.0,
        start_date: date = None,
        end_date: date = None
    ) -> Budget:
        """Create a new budget with validation."""
        if not category_repository.get_by_id(db, category_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        if amount_limit <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount limit must be greater than zero"
            )
        
        if period_type == PeriodType.CUSTOM:
            if not start_date or not end_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Custom period requires both start and end dates"
                )
            if end_date <= start_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End date must be after start date"
                )
        
        budget = budget_repository.create(
            db, user_id, category_id, Decimal(str(amount_limit)),
            period_type, Decimal(str(alert_threshold)), start_date, end_date
        )
        
        return self._enrich_budget_with_usage(db, budget)
    
    def update_budget(
        self,
        db: Session,
        budget_id: int,
        user_id: int,
        amount_limit: float = None,
        alert_threshold: float = None,
        period_type: PeriodType = None,
        start_date: date = None,
        end_date: date = None
    ) -> Budget:
        """Update an existing budget."""
        budget = budget_repository.get_by_id(db, budget_id, user_id)
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found"
            )
        
        if amount_limit is not None:
            budget.amount_limit = Decimal(str(amount_limit))
        if alert_threshold is not None:
            budget.alert_threshold = Decimal(str(alert_threshold))
        if period_type is not None:
            budget.period_type = period_type
        if start_date is not None:
            budget.start_date = start_date
        if end_date is not None:
            budget.end_date = end_date
        
        updated_budget = budget_repository.update(db, budget)
        return self._enrich_budget_with_usage(db, updated_budget)
    
    def delete_budget(self, db: Session, budget_id: int, user_id: int) -> None:
        """Delete a budget."""
        budget = budget_repository.get_by_id(db, budget_id, user_id)
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found"
            )
        
        budget_repository.delete(db, budget)
    
    def get_budget_by_id(self, db: Session, budget_id: int, user_id: int) -> Budget:
        """Get budget by ID with usage information."""
        budget = budget_repository.get_by_id(db, budget_id, user_id)
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found"
            )
        
        return self._enrich_budget_with_usage(db, budget)
    
    def get_all_budgets(self, db: Session, user_id: int) -> List[Budget]:
        """Get all budgets for a user with usage information."""
        budgets = budget_repository.get_all_by_user(db, user_id)
        return [self._enrich_budget_with_usage(db, budget) for budget in budgets]
    
    def get_budget_summary(
        self,
        db: Session,
        user_id: int,
        year: int,
        month: int = None,
        quarter: int = None
    ) -> dict:
        """Get budget summary for a period."""
        budgets = budget_repository.get_all_by_user(db, user_id)
        enriched_budgets = [self._enrich_budget_with_usage(db, budget) for budget in budgets]
        
        total_budget = sum(float(budget.amount_limit) for budget in enriched_budgets)
        total_spent = sum(float(getattr(budget, 'used_amount', 0)) for budget in enriched_budgets)
        
        period_str = self._format_period_string(year, month, quarter)
        
        return {
            "period": period_str,
            "total_budget": total_budget,
            "total_spent": total_spent,
            "budgets": enriched_budgets
        }
    
    def _enrich_budget_with_usage(self, db: Session, budget: Budget) -> Budget:
        """Add usage information to budget."""
        period_start, period_end = self._calculate_budget_period(budget)
        
        used_amount = transaction_repository.get_total_by_category_and_period(
            db, budget.user_id, budget.category_id, period_start, period_end
        )
        
        used_amount_float = float(used_amount)
        limit_float = float(budget.amount_limit)
        
        remaining = limit_float - used_amount_float
        usage_percentage = (used_amount_float / limit_float * 100) if limit_float > 0 else 0
        
        # Use budget's own alert_threshold instead of global config
        threshold = float(budget.alert_threshold) if budget.alert_threshold else (settings.budget_near_limit_threshold * 100)
        is_near_limit = usage_percentage >= threshold
        is_exceeded = usage_percentage >= (settings.budget_exceeded_threshold * 100)
        
        setattr(budget, 'used_amount', used_amount_float)
        setattr(budget, 'remaining_amount', remaining)
        setattr(budget, 'usage_percentage', usage_percentage)
        setattr(budget, 'is_near_limit', is_near_limit)
        setattr(budget, 'is_exceeded', is_exceeded)
        
        return budget
    
    def _calculate_budget_period(self, budget: Budget) -> Tuple[date, date]:
        """Calculate the current period for a budget."""
        today = date.today()
        
        if budget.period_type == PeriodType.MONTHLY:
            start_date = date(today.year, today.month, 1)
            if today.month == 12:
                end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)
            return start_date, end_date
        
        elif budget.period_type == PeriodType.WEEKLY:
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
            return start_date, end_date
        
        elif budget.period_type == PeriodType.CUSTOM:
            return budget.start_date or today, budget.end_date or today
        
        return today, today
    
    def _format_period_string(self, year: int, month: int = None, quarter: int = None) -> str:
        """Format period string for summary."""
        if month:
            return f"{year}-{month:02d}"
        elif quarter:
            return f"{year}-Q{quarter}"
        else:
            return str(year)


budget_service = BudgetService()
