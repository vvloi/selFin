"""Budget repository for database operations."""
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date
from decimal import Decimal
from app.models.budget import Budget, PeriodType


class BudgetRepository:
    """Repository for Budget entity database operations."""
    
    def create(
        self,
        db: Session,
        user_id: int,
        category_id: int,
        amount_limit: Decimal,
        period_type: PeriodType,
        alert_threshold: Decimal = Decimal("80.0"),
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Budget:
        """Create a new budget."""
        budget = Budget(
            user_id=user_id,
            category_id=category_id,
            amount_limit=amount_limit,
            alert_threshold=alert_threshold,
            period_type=period_type,
            start_date=start_date,
            end_date=end_date
        )
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return budget
    
    def get_by_id(self, db: Session, budget_id: int, user_id: int) -> Optional[Budget]:
        """Get budget by ID for a specific user."""
        return db.query(Budget).options(
            joinedload(Budget.category)
        ).filter(
            Budget.id == budget_id,
            Budget.user_id == user_id
        ).first()
    
    def get_all_by_user(self, db: Session, user_id: int) -> List[Budget]:
        """Get all budgets for a user."""
        return db.query(Budget).options(
            joinedload(Budget.category)
        ).filter(Budget.user_id == user_id).all()
    
    def update(self, db: Session, budget: Budget) -> Budget:
        """Update budget."""
        db.commit()
        db.refresh(budget)
        return budget
    
    def delete(self, db: Session, budget: Budget) -> None:
        """Delete budget."""
        db.delete(budget)
        db.commit()


budget_repository = BudgetRepository()
