"""Recurring transaction repository for database operations."""
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date
from decimal import Decimal
from app.models.recurring_transaction import RecurringTransaction, Frequency


class RecurringTransactionRepository:
    """Repository for RecurringTransaction entity database operations."""
    
    def create(
        self,
        db: Session,
        user_id: int,
        transaction_type: str,
        amount: Decimal,
        currency: str,
        frequency: Frequency,
        start_date: date,
        next_run_date: date,
        category_id: Optional[int] = None,
        wallet_id: Optional[int] = None,
        to_wallet_id: Optional[int] = None,
        description: Optional[str] = None,
        is_active: bool = True
    ) -> RecurringTransaction:
        """Create a new recurring transaction."""
        recurring = RecurringTransaction(
            user_id=user_id,
            type=transaction_type,
            amount=amount,
            currency=currency,
            frequency=frequency,
            start_date=start_date,
            next_run_date=next_run_date,
            category_id=category_id,
            wallet_id=wallet_id,
            to_wallet_id=to_wallet_id,
            description=description,
            is_active=is_active
        )
        db.add(recurring)
        db.commit()
        db.refresh(recurring)
        return recurring
    
    def get_by_id(self, db: Session, recurring_id: int, user_id: int) -> Optional[RecurringTransaction]:
        """Get recurring transaction by ID for a specific user."""
        return db.query(RecurringTransaction).options(
            joinedload(RecurringTransaction.category),
            joinedload(RecurringTransaction.wallet),
            joinedload(RecurringTransaction.to_wallet)
        ).filter(
            RecurringTransaction.id == recurring_id,
            RecurringTransaction.user_id == user_id
        ).first()
    
    def get_all_by_user(self, db: Session, user_id: int) -> List[RecurringTransaction]:
        """Get all recurring transactions for a user."""
        return db.query(RecurringTransaction).options(
            joinedload(RecurringTransaction.category),
            joinedload(RecurringTransaction.wallet),
            joinedload(RecurringTransaction.to_wallet)
        ).filter(RecurringTransaction.user_id == user_id).all()
    
    def get_due_recurring(self, db: Session, current_date: date) -> List[RecurringTransaction]:
        """Get all active recurring transactions that are due."""
        return db.query(RecurringTransaction).filter(
            RecurringTransaction.is_active == True,
            RecurringTransaction.next_run_date <= current_date
        ).all()
    
    def update(self, db: Session, recurring: RecurringTransaction) -> RecurringTransaction:
        """Update recurring transaction."""
        db.commit()
        db.refresh(recurring)
        return recurring
    
    def delete(self, db: Session, recurring: RecurringTransaction) -> None:
        """Delete recurring transaction."""
        db.delete(recurring)
        db.commit()


recurring_repository = RecurringTransactionRepository()
