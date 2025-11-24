"""Transaction service for business logic."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from decimal import Decimal
from typing import List, Tuple, Optional
from collections import defaultdict
from app.models.transaction import Transaction, TransactionType
from app.repositories.transaction_repository import transaction_repository
from app.repositories.wallet_repository import wallet_repository
from app.repositories.category_repository import category_repository


class TransactionService:
    """Service for transaction business logic."""
    
    def create_transaction(
        self,
        db: Session,
        user_id: int,
        transaction_type: TransactionType,
        amount: float,
        currency: str,
        transaction_date: datetime,
        category_id: Optional[int] = None,
        wallet_id: Optional[int] = None,
        to_wallet_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> Transaction:
        """Create a new transaction with validation."""
        self._validate_transaction_data(
            db, user_id, transaction_type, amount, category_id, wallet_id, to_wallet_id
        )
        
        amount_decimal = Decimal(str(amount))
        
        transaction = transaction_repository.create(
            db, user_id, transaction_type, amount_decimal, currency,
            transaction_date, category_id, wallet_id, to_wallet_id, description
        )
        
        self._update_wallet_balances(db, transaction_type, wallet_id, to_wallet_id, amount_decimal)
        
        return transaction
    
    def update_transaction(
        self,
        db: Session,
        transaction_id: int,
        user_id: int,
        transaction_type: Optional[TransactionType] = None,
        amount: Optional[float] = None,
        currency: Optional[str] = None,
        transaction_date: Optional[datetime] = None,
        category_id: Optional[int] = None,
        wallet_id: Optional[int] = None,
        to_wallet_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> Transaction:
        """Update an existing transaction."""
        transaction = transaction_repository.get_by_id(db, transaction_id, user_id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        self._revert_wallet_balances(db, transaction)
        
        if transaction_type is not None:
            transaction.type = transaction_type
        if amount is not None:
            transaction.amount = Decimal(str(amount))
        if currency is not None:
            transaction.currency = currency
        if transaction_date is not None:
            transaction.date = transaction_date
        if category_id is not None:
            transaction.category_id = category_id
        if wallet_id is not None:
            transaction.wallet_id = wallet_id
        if to_wallet_id is not None:
            transaction.to_wallet_id = to_wallet_id
        if description is not None:
            transaction.description = description
        
        updated_transaction = transaction_repository.update(db, transaction)
        
        self._update_wallet_balances(
            db, updated_transaction.type, updated_transaction.wallet_id,
            updated_transaction.to_wallet_id, updated_transaction.amount
        )
        
        return updated_transaction
    
    def delete_transaction(self, db: Session, transaction_id: int, user_id: int) -> None:
        """Delete a transaction."""
        transaction = transaction_repository.get_by_id(db, transaction_id, user_id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        self._revert_wallet_balances(db, transaction)
        transaction_repository.delete(db, transaction)
    
    def get_transactions_with_filters(
        self,
        db: Session,
        user_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        category_id: Optional[int] = None,
        wallet_id: Optional[int] = None,
        transaction_type: Optional[TransactionType] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        page: int = 1,
        size: int = 50
    ) -> Tuple[List[Transaction], int]:
        """Get transactions with filters and pagination."""
        min_decimal = Decimal(str(min_amount)) if min_amount is not None else None
        max_decimal = Decimal(str(max_amount)) if max_amount is not None else None
        return transaction_repository.get_with_filters(
            db, user_id, date_from, date_to, category_id, wallet_id, transaction_type,
            min_decimal, max_decimal, page, size
        )
    
    def get_daily_grouped_transactions(
        self,
        db: Session,
        user_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[dict]:
        """Get transactions grouped by day."""
        transactions = transaction_repository.get_grouped_by_day(db, user_id, date_from, date_to)
        return self._group_transactions_by_date(transactions)
    
    def get_weekly_grouped_transactions(
        self,
        db: Session,
        user_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[dict]:
        """Get transactions grouped by week."""
        transactions = transaction_repository.get_grouped_by_day(db, user_id, date_from, date_to)
        return self._group_transactions_by_week(transactions)
    
    def get_monthly_grouped_transactions(
        self,
        db: Session,
        user_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[dict]:
        """Get transactions grouped by month."""
        transactions = transaction_repository.get_grouped_by_day(db, user_id, date_from, date_to)
        return self._group_transactions_by_month(transactions)
    
    def _validate_transaction_data(
        self,
        db: Session,
        user_id: int,
        transaction_type: TransactionType,
        amount: float,
        category_id: Optional[int],
        wallet_id: Optional[int],
        to_wallet_id: Optional[int]
    ) -> None:
        """Validate transaction data."""
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be greater than zero"
            )
        
        if transaction_type == TransactionType.TRANSFER:
            if not wallet_id or not to_wallet_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Transfer requires both source and destination wallets"
                )
            if wallet_id == to_wallet_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Source and destination wallets must be different"
                )
        
        if category_id:
            category = category_repository.get_by_id(db, category_id, user_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found"
                )
        
        if wallet_id:
            wallet = wallet_repository.get_by_id(db, wallet_id, user_id)
            if not wallet:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Wallet not found"
                )
    
    def _update_wallet_balances(
        self,
        db: Session,
        transaction_type: TransactionType,
        wallet_id: Optional[int],
        to_wallet_id: Optional[int],
        amount: Decimal
    ) -> None:
        """Update wallet balances based on transaction type."""
        if transaction_type == TransactionType.INCOME and wallet_id:
            wallet_repository.update_balance(db, wallet_id, amount)
        elif transaction_type == TransactionType.EXPENSE and wallet_id:
            wallet_repository.update_balance(db, wallet_id, -amount)
        elif transaction_type == TransactionType.TRANSFER and wallet_id and to_wallet_id:
            wallet_repository.update_balance(db, wallet_id, -amount)
            wallet_repository.update_balance(db, to_wallet_id, amount)
    
    def _revert_wallet_balances(self, db: Session, transaction: Transaction) -> None:
        """Revert wallet balances for a transaction."""
        if transaction.type == TransactionType.INCOME and transaction.wallet_id:
            wallet_repository.update_balance(db, transaction.wallet_id, -transaction.amount)
        elif transaction.type == TransactionType.EXPENSE and transaction.wallet_id:
            wallet_repository.update_balance(db, transaction.wallet_id, transaction.amount)
        elif transaction.type == TransactionType.TRANSFER and transaction.wallet_id and transaction.to_wallet_id:
            wallet_repository.update_balance(db, transaction.wallet_id, transaction.amount)
            wallet_repository.update_balance(db, transaction.to_wallet_id, -transaction.amount)
    
    def _group_transactions_by_date(self, transactions: List[Transaction]) -> List[dict]:
        """Group transactions by date."""
        grouped = defaultdict(lambda: {"total_income": 0.0, "total_expense": 0.0, "transactions": []})
        
        for transaction in transactions:
            date_str = transaction.date.date().isoformat()
            grouped[date_str]["transactions"].append(transaction)
            
            if transaction.type == TransactionType.INCOME:
                grouped[date_str]["total_income"] += float(transaction.amount)
            elif transaction.type == TransactionType.EXPENSE:
                grouped[date_str]["total_expense"] += float(transaction.amount)
        
        return [
            {
                "date": date_str,
                "total_income": data["total_income"],
                "total_expense": data["total_expense"],
                "transactions": data["transactions"]
            }
            for date_str, data in sorted(grouped.items(), reverse=True)
        ]
    
    def _group_transactions_by_week(self, transactions: List[Transaction]) -> List[dict]:
        """Group transactions by week."""
        grouped = defaultdict(lambda: {"total_income": 0.0, "total_expense": 0.0, "transactions": []})
        
        for transaction in transactions:
            year, week, _ = transaction.date.isocalendar()
            key = (year, week)
            grouped[key]["transactions"].append(transaction)
            
            if transaction.type == TransactionType.INCOME:
                grouped[key]["total_income"] += float(transaction.amount)
            elif transaction.type == TransactionType.EXPENSE:
                grouped[key]["total_expense"] += float(transaction.amount)
        
        result = []
        for (year, week), data in sorted(grouped.items(), reverse=True):
            result.append({
                "year": year,
                "week": week,
                "total_income": data["total_income"],
                "total_expense": data["total_expense"],
                "transactions": data["transactions"]
            })
        
        return result
    
    def _group_transactions_by_month(self, transactions: List[Transaction]) -> List[dict]:
        """Group transactions by month."""
        grouped = defaultdict(lambda: {"total_income": 0.0, "total_expense": 0.0, "transactions": []})
        
        for transaction in transactions:
            key = (transaction.date.year, transaction.date.month)
            grouped[key]["transactions"].append(transaction)
            
            if transaction.type == TransactionType.INCOME:
                grouped[key]["total_income"] += float(transaction.amount)
            elif transaction.type == TransactionType.EXPENSE:
                grouped[key]["total_expense"] += float(transaction.amount)
        
        result = []
        for (year, month), data in sorted(grouped.items(), reverse=True):
            result.append({
                "year": year,
                "month": month,
                "total_income": data["total_income"],
                "total_expense": data["total_expense"],
                "transactions": data["transactions"]
            })
        
        return result


transaction_service = TransactionService()
