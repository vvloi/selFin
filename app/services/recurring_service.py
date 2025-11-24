"""Recurring transaction service for business logic."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from typing import List, Optional
from app.models.recurring_transaction import RecurringTransaction, Frequency
from app.models.transaction import TransactionType
from app.repositories.recurring_repository import recurring_repository
from app.services.transaction_service import transaction_service


class RecurringTransactionService:
    """Service for recurring transaction business logic."""
    
    def create_recurring_transaction(
        self,
        db: Session,
        user_id: int,
        transaction_type: TransactionType,
        amount: float,
        currency: str,
        frequency: Frequency,
        start_date: date,
        category_id: Optional[int] = None,
        wallet_id: Optional[int] = None,
        to_wallet_id: Optional[int] = None,
        description: Optional[str] = None,
        is_active: bool = True
    ) -> RecurringTransaction:
        """Create a new recurring transaction."""
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be greater than zero"
            )
        
        next_run_date = self._calculate_next_run_date(start_date, frequency)
        
        recurring = recurring_repository.create(
            db, user_id, transaction_type.value, Decimal(str(amount)), currency,
            frequency, start_date, next_run_date, category_id, wallet_id,
            to_wallet_id, description, is_active
        )
        
        return recurring
    
    def update_recurring_transaction(
        self,
        db: Session,
        recurring_id: int,
        user_id: int,
        transaction_type: Optional[TransactionType] = None,
        amount: Optional[float] = None,
        currency: Optional[str] = None,
        frequency: Optional[Frequency] = None,
        start_date: Optional[date] = None,
        category_id: Optional[int] = None,
        wallet_id: Optional[int] = None,
        to_wallet_id: Optional[int] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> RecurringTransaction:
        """Update an existing recurring transaction."""
        recurring = recurring_repository.get_by_id(db, recurring_id, user_id)
        
        if not recurring:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurring transaction not found"
            )
        
        if transaction_type is not None:
            recurring.type = transaction_type.value
        if amount is not None:
            recurring.amount = Decimal(str(amount))
        if currency is not None:
            recurring.currency = currency
        if frequency is not None:
            recurring.frequency = frequency
            recurring.next_run_date = self._calculate_next_run_date(
                recurring.start_date, frequency
            )
        if start_date is not None:
            recurring.start_date = start_date
        if category_id is not None:
            recurring.category_id = category_id
        if wallet_id is not None:
            recurring.wallet_id = wallet_id
        if to_wallet_id is not None:
            recurring.to_wallet_id = to_wallet_id
        if description is not None:
            recurring.description = description
        if is_active is not None:
            recurring.is_active = is_active
        
        return recurring_repository.update(db, recurring)
    
    def delete_recurring_transaction(self, db: Session, recurring_id: int, user_id: int) -> None:
        """Delete a recurring transaction."""
        recurring = recurring_repository.get_by_id(db, recurring_id, user_id)
        
        if not recurring:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurring transaction not found"
            )
        
        recurring_repository.delete(db, recurring)
    
    def get_recurring_by_id(
        self,
        db: Session,
        recurring_id: int,
        user_id: int
    ) -> RecurringTransaction:
        """Get recurring transaction by ID."""
        recurring = recurring_repository.get_by_id(db, recurring_id, user_id)
        
        if not recurring:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurring transaction not found"
            )
        
        return recurring
    
    def get_all_recurring(self, db: Session, user_id: int) -> List[RecurringTransaction]:
        """Get all recurring transactions for a user."""
        return recurring_repository.get_all_by_user(db, user_id)
    
    def execute_recurring_transaction(
        self,
        db: Session,
        recurring_id: int,
        user_id: int
    ) -> dict:
        """Manually execute a recurring transaction."""
        recurring = recurring_repository.get_by_id(db, recurring_id, user_id)
        
        if not recurring:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurring transaction not found"
            )
        
        from datetime import datetime
        
        transaction = transaction_service.create_transaction(
            db, user_id, TransactionType(recurring.type), float(recurring.amount),
            recurring.currency, datetime.now(), recurring.category_id,
            recurring.wallet_id, recurring.to_wallet_id, recurring.description
        )
        
        recurring.last_run_date = date.today()
        recurring.next_run_date = self._calculate_next_run_date(
            date.today(), recurring.frequency
        )
        recurring_repository.update(db, recurring)
        
        return transaction
    
    def process_due_recurring_transactions(self, db: Session) -> List[dict]:
        """Process all due recurring transactions (called by scheduler)."""
        due_recurring = recurring_repository.get_due_recurring(db, date.today())
        created_transactions = []
        
        for recurring in due_recurring:
            try:
                from datetime import datetime
                
                transaction = transaction_service.create_transaction(
                    db, recurring.user_id, TransactionType(recurring.type),
                    float(recurring.amount), recurring.currency, datetime.now(),
                    recurring.category_id, recurring.wallet_id, recurring.to_wallet_id,
                    recurring.description
                )
                
                recurring.last_run_date = date.today()
                recurring.next_run_date = self._calculate_next_run_date(
                    date.today(), recurring.frequency
                )
                recurring_repository.update(db, recurring)
                
                created_transactions.append(transaction)
            except Exception:
                continue
        
        return created_transactions
    
    def _calculate_next_run_date(self, current_date: date, frequency: Frequency) -> date:
        """Calculate the next run date based on frequency."""
        if frequency == Frequency.DAILY:
            return current_date + timedelta(days=1)
        elif frequency == Frequency.WEEKLY:
            return current_date + timedelta(weeks=1)
        elif frequency == Frequency.MONTHLY:
            return current_date + relativedelta(months=1)
        elif frequency == Frequency.YEARLY:
            return current_date + relativedelta(years=1)
        
        return current_date


recurring_service = RecurringTransactionService()
